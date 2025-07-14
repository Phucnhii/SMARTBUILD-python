"""from ultralytics import YOLO
import cv2
import os

# Gợi ý sản phẩm cho các nhãn
SUGGESTIONS = {
    "damp": [
        "Sơn chống thấm gốc nước ACRYL-Guard",
        "Màng chống thấm BitumFlex",
        "Vữa chống thấm tinh thể XYPEX"],
    "door": [
        "Cửa nhôm kính XINGFA 2 lớp kính",
        "Cửa thép vân gỗ chống cháy 70 phút",
        "Cửa uPVC lõi thép chịu lực"],
    "none": [
        "Không phát hiện vấn đề rõ ràng – liên hệ kỹ thuật viên để khảo sát"],
}

# Load mô hình YOLOv8 (dùng model nhẹ để thử)
model = YOLO("yolov8n.pt")  # hoặc yolov8s.pt

def analyze(image_path: str) -> dict:
    #Phân tích ảnh thật bằng mô hình YOLOv8.

    results = model(image_path)[0]  # lấy kết quả đầu tiên
    detected_labels = [model.names[int(cls)] for cls in results.boxes.cls]

    # Xử lý suy luận đơn giản từ object được phát hiện
    if any(label.lower() in ["window", "door"] for label in detected_labels):
        label = "door"
    elif any(label.lower() in ["water", "stain", "damp", "mold"] for label in detected_labels):
        label = "damp"
    else:
        label = "none"

    # Tính confidence trung bình
    confs = [float(c) for c in results.boxes.conf]
    confidence = round(sum(confs) / len(confs), 2) if confs else 0.85

    return {
        "label": label,
        "confidence": confidence,
        "recommendations": SUGGESTIONS[label],
    }"""
"""Mô-đun giả lập Computer Vision.
   Ở production, thay bằng YOLOv8 / SAM, v.v.
"""
from random import choice, randint

SUGGESTIONS = {
    "Thấm nước": [
        "Sơn chống thấm gốc xi măng SikaTop Seal 107",
        "Lớp phủ chống thấm đàn hồi KOVA CT-11A",
        "Màng khò nóng Bitum chống thấm Polyglass"],
    "Ăn mòn": [
        "Sơn epoxy chống ăn mòn Jotun Jotamastic 87",
        "Vữa sửa chữa chống ăn mòn Sika MonoTop-610",
        "Chất ức chế ăn mòn cho cốt thép MCI-2020"],
    "Nứt bêtông": [
        "Keo trám khe nứt Sikadur-752",
        "Băng cản nước PVC chống rò rỉ mạch ngừng",
        "Vữa sửa chữa có tính đàn hồi Flexcrete"],
    "Rò rỉ mái": [
        "Sơn chống thấm mái nhà ASIAN CT-04",
        "Tấm nhựa PVC chống thấm dùng cho mái",
        "Chất chống thấm gốc polyurethane Bostik"],
    "Không rõ": [
        "Không phát hiện vấn đề rõ ràng – liên hệ kỹ thuật viên để khảo sát thêm"],
}

def analyze(image_path: str) -> dict:
    """Trả về nhãn giả + gợi ý sản phẩm."""
    label = choice(["Thấm nước", "Ăn mòn", "Nứt bêtông", "Rò rỉ mái", "Không rõ"])
    confidence = round(randint(80, 99) / 100, 2)
    return {
        "label": label,
        "confidence": confidence,
        "recommendations": SUGGESTIONS[label],
    }