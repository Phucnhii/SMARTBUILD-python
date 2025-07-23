import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = 'SmartBuild_AI'

# Kiểm tra nếu không có MONGODB_URI trong file .env
if not MONGODB_URI:
    raise ValueError("MONGODB_URI không được tìm thấy trong file .env")

try:
    # Kết nối đến MongoDB Atlas
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    # Test kết nối
    client.admin.command('ping')
    print(f"✅ Kết nối thành công đến MongoDB Atlas - Database: {DATABASE_NAME}")
    
except Exception as e:
    print(f"❌ Lỗi kết nối MongoDB: {str(e)}")
    raise

# Hàm helper để lấy database
def get_database():
    """Trả về database instance"""
    return db
