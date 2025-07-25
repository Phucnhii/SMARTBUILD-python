from flask import Flask, render_template, request, jsonify, make_response, send_from_directory,flash, url_for, redirect
from werkzeug.utils import secure_filename
import os
from datetime import timedelta, datetime
import cv2
from model import analyze
import logging
from werkzeug.exceptions import RequestEntityTooLarge
import csv
from gemini_api import call_gemini 
import requests
from dotenv import load_dotenv
from connect_database import get_database
from gridfs import GridFS
from bson import ObjectId
import io
from admin import admin_bp, setup_download_routes

load_dotenv()
# Lấy biến môi trường FRIENDLYCAPTCHA_SECRET
FRIENDLYCAPTCHA_SECRET = os.getenv('FRIENDLYCAPTCHA_SECRET')

# Kiểm tra kết nối MongoDB khi khởi động app
try:
    db = get_database()
    fs_recruitment = GridFS(db, collection="cv_files")
    fs_contact = GridFS(db, collection="contact_images")
    db.command('ping')
    logging.info("✅ MongoDB connection successful")
    print("✅ Connected to MongoDB Atlas - Database: SmartBuild_AI")
except Exception as e:
    logging.error(f"❌ MongoDB connection failed: {str(e)}")
    print(f"❌ MongoDB connection failed: {str(e)}")
    # App vẫn có thể chạy nhưng sẽ không lưu được vào MongoDB

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename='logs/access.log', level=logging.INFO, format='%(asctime)s - %(message)s')

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Đăng ký Blueprint admin
app.register_blueprint(admin_bp)

# Setup download routes
setup_download_routes(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Upload CV
app.secret_key = 'supersecret'
ALLOWED_CV_EXTENSIONS = {"pdf"}
UPLOAD_CV_FOLDER = os.path.join(UPLOAD_FOLDER, "cv")
os.makedirs(UPLOAD_CV_FOLDER, exist_ok=True)

# Upload img contact
ALLOWED_CONTACT_EXTENSIONS = {"png", "jpg", "jpeg"}
UPLOAD_CONTACT_FOLDER = os.path.join(UPLOAD_FOLDER, "contact_img")
os.makedirs(UPLOAD_CONTACT_FOLDER, exist_ok=True)

# ---------- Helpers ----------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload CV
def allowed_cv_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_CV_EXTENSIONS

def validate_images(images, max_files=5):
    """Kiểm tra số lượng và loại file ảnh"""
    if len(images) == 0:
        return False, "Vui lòng tải lên ít nhất một hình ảnh"
    if len(images) > max_files:
        return False, f"Chỉ được tải lên tối đa {max_files} ảnh"
    return True, ""

# ---------- Routes ----------

@app.after_request
def apply_security_headers(response):
    # Set first‑party cookie nếu chưa có
    if not request.cookies.get("sb_uid"):
        response.set_cookie(
            "sb_uid",
            os.urandom(8).hex(),
            max_age=30 * 24 * 60 * 60,
            secure=True,
            httponly=True,
            samesite="Strict",
        )
    
    # Các headers bảo mật
    response.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; font-src 'self' data:; connect-src 'self' https://api.friendlycaptcha.com https://assets10.lottiefiles.com/packages/lf20_yd9yoprx.json; script-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://js.friendlycaptcha.com https://unpkg.com/lottie-web@5.10.2/build/player/lottie.min.js; worker-src blob:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
        "Referrer-Policy": "no-referrer",
    })
    return response

@app.route("/")
def index():
    resp = make_response(render_template("index.html"))
    return resp

# Route để serve ảnh contact từ GridFS
@app.route("/contact/image/<file_id>")
def serve_contact_image(file_id):
    try:
        # Lấy file từ GridFS
        grid_out = fs_contact.get(ObjectId(file_id))
        
        # Tạo response với đúng content type
        response = make_response(grid_out.read())
        response.headers['Content-Type'] = grid_out.content_type or 'image/jpeg'
        response.headers['Content-Disposition'] = f'inline; filename="{grid_out.filename}"'
        
        return response
    except Exception as e:
        logging.error(f"Failed to serve contact image {file_id}: {str(e)}")
        return jsonify({"error": "Image not found"}), 404

# API để lấy danh sách contact submissions (cho admin)
@app.route("/api/contacts")
def api_contacts():
    try:
        contacts = list(db.contact_submissions.find().sort("submitted_at", -1))
        
        # Convert ObjectId to string để JSON serialize được
        for contact in contacts:
            contact['_id'] = str(contact['_id'])
            contact['image_ids'] = [str(img_id) for img_id in contact.get('image_ids', [])]
            contact['submitted_at'] = contact['submitted_at'].isoformat()
            
        return jsonify(contacts)
    except Exception as e:
        logging.error(f"Failed to get contacts: {str(e)}")
        return jsonify({"error": "Failed to get contacts"}), 500 

@app.route("/", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            # Xác thực CAPTCHA
            solution = request.form.get('frc-captcha-solution')
            if not solution:
                flash("Vui lòng hoàn thành CAPTCHA", "error")
                return redirect(url_for("contact"))

            # Gửi request đến FriendlyCaptcha để xác thực
            verify_response = requests.post(
                'https://api.friendlycaptcha.com/api/v1/siteverify',
                data={
                    'secret': FRIENDLYCAPTCHA_SECRET,
                    'solution': solution
                }
            )

            verify_result = verify_response.json()
            if not verify_result.get("success"):
                flash("CAPTCHA không hợp lệ. Vui lòng thử lại.", "error")
                return redirect(url_for("contact"))

            # Lấy dữ liệu từ form
            form_data = {
                'last_name': request.form.get('last-name'),
                'first_name': request.form.get('first-name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'country': request.form.get('country'),
                'problem': request.form.get('problem'),
                'construction_type': request.form.get('construction_type'),
                'request_type': request.form.get('request_type'),
                'problem_description': request.form.get('problem_description')
            }

            # Xử lý upload ảnh vào GridFS
            images = request.files.getlist('construction_images')
            is_valid, message = validate_images(images)
            if not is_valid:
                flash(message, 'error')
                return redirect(url_for('contact'))

            # Lưu ảnh vào GridFS và lấy file IDs
            image_ids = []
            for idx, image in enumerate(images[:5]):
                if image and allowed_file(image.filename):
                    try:
                        # Tạo tên file duy nhất
                        ext = image.filename.rsplit('.', 1)[1].lower()
                        base_name = secure_filename(f"{form_data['email']}_{idx}")
                        filename = f"{base_name}.{ext}"
                        
                        # Lưu vào GridFS với metadata
                        file_id = fs_contact.put(
                            image.stream,
                            filename=filename,
                            content_type=image.content_type,
                            contact_email=form_data['email'],
                            upload_index=idx
                        )
                        image_ids.append(file_id)
                        logging.info(f"✅ Contact image uploaded to GridFS - ID: {file_id}")
                        
                    except Exception as e:
                        logging.error(f"❌ Failed to upload contact image: {str(e)}")
                        flash("Đã có lỗi xảy ra khi lưu ảnh.")
                        return redirect(url_for("contact"))
                else:
                    flash('Chỉ chấp nhận file ảnh (PNG, JPG, JPEG)', 'error')
                    return redirect(url_for('contact'))

            # Lưu contact submission vào MongoDB
            try:
                contact_data = {
                    'email': form_data['email'],
                    'last_name': form_data['last_name'],
                    'first_name': form_data['first_name'],
                    'phone': form_data['phone'],
                    'country': form_data['country'],
                    'problem': form_data['problem'],
                    'construction_type': form_data['construction_type'],
                    'request_type': form_data['request_type'],
                    'problem_description': form_data['problem_description'],
                    'image_ids': image_ids,  # Array của GridFS file IDs
                    'image_count': len(image_ids),  # Số lượng ảnh
                    'ip_address': request.remote_addr,
                    'submitted_at': datetime.utcnow(),
                    'status': 'pending',
                    'user_agent': request.headers.get('User-Agent', '')
                }
                
                result = db.contact_submissions.insert_one(contact_data)
                logging.info(f"✅ Contact submission saved to MongoDB - ID: {result.inserted_id}")
                
            except Exception as e:
                logging.error(f"❌ Failed to save contact submission: {str(e)}")
                # Nếu lưu MongoDB fail, xóa các ảnh đã upload
                for file_id in image_ids:
                    try:
                        fs_contact.delete(file_id)
                    except:
                        pass
                flash("Đã có lỗi xảy ra khi lưu thông tin liên hệ.")
                return redirect(url_for("contact"))

            # Ghi log thông tin
            logging.info(
                f"[CONTACT] From: {form_data['email']}, IP: {request.remote_addr}, "
                f"Problem: {form_data['problem']}, Construction: {form_data['construction_type']}"
            )

            # TODO: xử lý thêm như gửi email, lưu DB...

            flash('Yêu cầu của bạn đã được gửi thành công! Chúng tôi sẽ liên hệ lại sớm.', 'success')
            return redirect(url_for('contact'))

        except Exception as e:
            logging.exception("Error processing contact form")
            flash('Đã có lỗi xảy ra khi gửi yêu cầu. Vui lòng thử lại.', 'error')
            return redirect(url_for('contact'))

    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        logging.info(f"User uploaded file: {filename}, IP: {request.remote_addr}")

        # Gọi model AI
        result = analyze(save_path)
        # Xoá file tạm
        os.remove(save_path)

        return jsonify(result)
    return jsonify({"error": "File type not allowed"}), 400

@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"]
    logging.info(f"Chatbot message: {user_message}, IP: {request.remote_addr}")

    try:
        # Gọi Gemini API
        bot_response = call_gemini(user_message)
        return jsonify({"response": bot_response})
    except Exception as e:
        logging.error(f"Gemini API error: {str(e)}")
        return jsonify({"error": "Failed to get response from Gemini API"}), 500

# Serve static files (only dev – production nên qua nginx)
@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(app.static_folder, path)

# Page khác
@app.route("/intro")
def intro():
    return render_template("intro.html") 

@app.route("/recruitment", methods=["GET", "POST"])
def recruitment():
    if request.method == "POST":
        for position in ['cv-devops', 'cv-ai', 'cv-frontend', 'cv-backend', 'cv-security']:
            if position in request.files:
                file = request.files[position]
                if file.filename == "":
                    flash("Vui lòng chọn file PDF.")
                    return redirect(url_for("recruitment"))

                if file and allowed_cv_file(file.filename):
                    filename = secure_filename(file.filename)
                    try:
                        # Sử dụng fs_recruitment đã khởi tạo sẵn
                        # Lưu file vào GridFS
                        file_id = fs_recruitment.put(file.stream, filename=filename, content_type=file.content_type)

                        # Tạo metadata
                        cv_data = {
                            'position': position,
                            'original_filename': file.filename,
                            'saved_filename': filename,
                            'file_id': file_id,  # ID GridFS
                            'file_size': file.content_length or 0,
                            'ip_address': request.remote_addr,
                            'submitted_at': datetime.utcnow(),
                            'status': 'received',
                            'user_agent': request.headers.get('User-Agent', ''),
                        }

                        result = db.cv_submissions.insert_one(cv_data)
                        logging.info(f"✅ CV uploaded to GridFS - ID: {file_id}")
                        logging.info(f"✅ CV metadata saved to MongoDB - ID: {result.inserted_id}")

                    except Exception as e:
                        logging.error(f"❌ Failed to upload CV: {str(e)}")
                        flash("Đã có lỗi xảy ra khi lưu hồ sơ.")
                        return redirect(url_for("recruitment"))

                    flash(f"Đã nhận hồ sơ cho vị trí {position.replace('cv-', '').upper()}.")
                    return redirect(url_for("recruitment"))

                else:
                    flash("Chỉ chấp nhận file PDF.")
                    return redirect(url_for("recruitment"))

    return render_template("recruitment.html")

@app.route("/product")
def product():
    return render_template("product.html") 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            # Xác thực CAPTCHA
            solution = request.form.get('frc-captcha-solution')
            if not solution:
                flash("Vui lòng hoàn thành CAPTCHA", "error")
                return redirect(url_for("login"))

            # Gửi request đến FriendlyCaptcha để xác thực
            verify_response = requests.post(
                'https://api.friendlycaptcha.com/api/v1/siteverify',
                data={
                    'secret': FRIENDLYCAPTCHA_SECRET,
                    'solution': solution
                }
            )

            verify_result = verify_response.json()
            if not verify_result.get("success"):
                flash("CAPTCHA không hợp lệ. Vui lòng thử lại.", "error")
                return redirect(url_for("contact"))
            
        except Exception as e:
            flash(f"Lỗi hệ thống: {str(e)}", "error")
            return redirect(url_for("login"))
        
    return render_template("login.html") 

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("Ảnh tải lên vượt quá giới hạn 2MB.", "error")
    return redirect(url_for('contact'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)