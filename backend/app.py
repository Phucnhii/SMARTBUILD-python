from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
import cv2
from model import analyze
import logging

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename='logs/access.log', level=logging.INFO, format='%(asctime)s - %(message)s')

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- Helpers ----------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route("/recruitment")
def recruitment():
    return render_template("recruitment.html") 

@app.route("/contact")
def contact():
    return render_template("contact.html") 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)