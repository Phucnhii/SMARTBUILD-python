# SmartBuild AI – Demo

Demo hệ thống tư vấn vật liệu chống thấm & cửa bằng AI, bao gồm:
* **Flask backend** (Python)
* **Computer Vision mẫu** (YOLOv8 giả lập)
* **Cookie first‑party** để cá nhân hoá
* **Triển khai Docker + Nginx**

## Cài đặt nhanh
```bash
# 1. Tạo và kích hoạt venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Cài requirements
pip install -r backend/requirements.txt

# 3. Chạy server (Dev)
python backend/app.py

# 4. Mở trình duyệt tại http://localhost:5000/