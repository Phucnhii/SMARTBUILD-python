from flask import Flask, render_template, request, jsonify, make_response, send_from_directory,flash, url_for, redirect
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
import cv2
from model import analyze
import logging
from werkzeug.exceptions import RequestEntityTooLarge
import csv

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename='logs/access.log', level=logging.INFO, format='%(asctime)s - %(message)s')

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

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

@app.route("/")
def index():
    resp = make_response(render_template("index.html"))
    # Set first‑party cookie nếu chưa có
    if not request.cookies.get("sb_uid"):
        resp.set_cookie(
            "sb_uid",
            os.urandom(8).hex(),
            max_age=30 * 24 * 60 * 60,  # 30 ngày
            secure=True,
            httponly=True,
            samesite="Strict",
        )
    # Headers ATTT
    resp.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "no-referrer",
    })
    return resp

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
                    folder = os.path.join(UPLOAD_CV_FOLDER, position)
                    os.makedirs(folder, exist_ok=True)
                    save_path = os.path.join(folder, filename)
                    file.save(save_path)

                    logging.info(f"CV submitted: {filename} for {position}, IP: {request.remote_addr}")
                    flash(f"Đã nhận hồ sơ cho vị trí {position.replace('cv-', '').upper()}.")
                    return redirect(url_for("recruitment"))
                else:
                    flash("Chỉ chấp nhận file PDF.")
                    return redirect(url_for("recruitment"))

    return render_template("recruitment.html")


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("Ảnh tải lên vượt quá giới hạn 2MB.", "error")
    return redirect(url_for('contact'))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
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

            # Xử lý upload ảnh
            images = request.files.getlist('construction_images')
            is_valid, message = validate_images(images)
            if not is_valid:
                flash(message, 'error')
                return redirect(url_for('contact'))

            saved_images = []
            for idx, image in enumerate(images[:5]):
                if image and allowed_file(image.filename):
                    # Đảm bảo tên file không chứa kí tự độc hại
                    ext = image.filename.rsplit('.', 1)[1].lower()
                    base_name = secure_filename(f"{form_data['email']}_{idx}")
                    filename = f"{base_name}.{ext}"
                    save_path = os.path.join(UPLOAD_CONTACT_FOLDER, filename)
                    image.save(save_path)
                    saved_images.append(save_path)
                else:
                    flash('Chỉ chấp nhận file ảnh (PNG, JPG, JPEG)', 'error')
                    return redirect(url_for('contact'))
                import csv

                # Lưu liên hệ về
                UPLOAD_CONTACT_DATA = os.path.join(app.config["UPLOAD_FOLDER"], "contact_data")
                os.makedirs(UPLOAD_CONTACT_DATA, exist_ok=True)
                CONTACT_CSV = os.path.join(UPLOAD_CONTACT_DATA, "contact_submissions.csv")

                # Sanitize email để dùng làm định danh (nếu cần)
                safe_email = secure_filename(form_data['email']) if form_data['email'] else "unknown"

                # Ghi vào file CSV
                with open(CONTACT_CSV, "a", newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        safe_email,
                        form_data['last_name'],
                        form_data['first_name'],
                        form_data['phone'],
                        form_data['country'],
                        form_data['problem'],
                        form_data['construction_type'],
                        form_data['request_type'],
                        form_data['problem_description'],
                        ";".join(saved_images),  # Đường dẫn ảnh
                        request.remote_addr       # IP người gửi
            ])

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

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)