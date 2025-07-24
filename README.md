# SmartBuild AI – Demo

Demo hệ thống tư vấn vật liệu chống thấm bằng AI, bao gồm:
* **Flask backend** (Python)
* **Computer Vision mẫu** (YOLOv8 giả lập)
* **MongoDB Atlas** - Lưu trữ CV và dữ liệu
* **Admin Panel** - Quản lý CV và thống kê
* **Triển khai Docker + Nginx**

## Cài đặt nhanh
```bash
# 1. Tạo và kích hoạt venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Cài requirements
pip install -r backend/requirements.txt

# 3. Cấu hình MongoDB Atlas trong file .env
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/SmartBuild_AI

# 4. Chạy server (Dev)
python backend/app.py

# 5. Mở trình duyệt:
# - Trang chủ: http://localhost:5000/
# - Admin: http://localhost:5000/admin
```

## Tính năng Admin
- **Dashboard:** `/admin` - Trang chủ admin
- **Quản lý CV:** `/admin/cvs` - Xem, download, cập nhật trạng thái CV
- **Download CV:** `/download/cv/{file_id}` - Download file PDF
- **Thống kê:** `/admin/stats` - Báo cáo số liệu

## Cấu trúc Database (MongoDB)
- **cv_submissions:** Metadata CV đã nộp
- **GridFS:** Lưu trữ file PDF
- **contact_submissions:** Form liên hệ (nếu có)mo

Demo hệ thống tư vấn vật liệu chống thấm bằng AI, bao gồm:
* **Flask backend** (Python)
* **Computer Vision mẫu** (YOLOv8 giả lập)
* **Triển khai Docker + Nginx**
