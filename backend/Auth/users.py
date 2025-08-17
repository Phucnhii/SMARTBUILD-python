from flask import Blueprint, request, jsonify
from connect_database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api')
db = get_database()
users = db.users 

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least 1 uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least 1 lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least 1 number"
    return True, "Valid"

# API đăng ký
@auth_bp.route("/signup", methods=["POST"])
def signup_api():
    # return jsonify({"message": "Success"})
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    print(f"Received data: {data}")  # Debugging line
    if not email or not password or not first_name or not last_name:
        return jsonify({"error": "Please fill out all information"}), 400

    if not validate_email(email):
        return jsonify({"error": "Wrong email"}), 400

    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({"error": message}), 400

    if users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    hashed_pw = generate_password_hash(password)
    user = {
        "email": email,
        "password": hashed_pw,
        "created_at": datetime.utcnow(),
        "firstName": first_name,
        "lastName": last_name,
        "last_login": None, 
    }
    users.insert_one(user)
    return jsonify({"message": "Sign up successful"}), 201

# API Đăng nhập
@auth_bp.route("/login", methods=["POST"])
def login_api():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and Password are required"}), 400
    if not validate_email(email):
        return jsonify({"error": "Wrong email format"}), 400
    user = users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Wrong email or Password"}), 400

    users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    return jsonify({
        "message": "Login successful",
        "user_id": str(user["_id"])
    }), 200

# @auth_bp.route('/logout', methods=['POST'])
# def logout():
#     """API đăng xuất"""
#     try:
#         session.clear()
#         return jsonify({
#             'success': True,
#             'message': 'Đăng xuất thành công'
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Lỗi server: {str(e)}'
#         }), 500

# @auth_bp.route('/verify-email/<token>', methods=['GET'])
# def verify_email(token):
#     """API xác thực email"""
#     try:
#         result = user_manager.verify_email(token)
        
#         if result['success']:
#             return jsonify({
#                 'success': True,
#                 'message': result['message']
#             }), 200
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': result['message']
#             }), 400
            
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Lỗi server: {str(e)}'
#         }), 500

# @auth_bp.route('/forgot-password', methods=['POST'])
# def forgot_password():
#     """API quên mật khẩu"""
#     try:
#         data = request.get_json()
#         email = data.get('email', '').strip().lower()
        
#         if not email:
#             return jsonify({
#                 'success': False,
#                 'message': 'Email là bắt buộc'
#             }), 400
        
#         if not validate_email(email):
#             return jsonify({
#                 'success': False,
#                 'message': 'Email không hợp lệ'
#             }), 400
        
#         result = user_manager.create_password_reset_token(email)
        
#         return jsonify({
#             'success': result['success'],
#             'message': result['message']
#         }), 200 if result['success'] else 400
        
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Lỗi server: {str(e)}'
#         }), 500

# @auth_bp.route('/reset-password', methods=['POST'])
# def reset_password():
#     """API reset mật khẩu"""
#     try:
#         data = request.get_json()
#         token = data.get('token', '')
#         new_password = data.get('new_password', '')
        
#         if not token or not new_password:
#             return jsonify({
#                 'success': False,
#                 'message': 'Token và mật khẩu mới là bắt buộc'
#             }), 400
        
#         # Validate new password
#         is_valid, msg = validate_password(new_password)
#         if not is_valid:
#             return jsonify({
#                 'success': False,
#                 'message': msg
#             }), 400
        
#         result = user_manager.reset_password(token, new_password)
        
#         return jsonify({
#             'success': result['success'],
#             'message': result['message']
#         }), 200 if result['success'] else 400
        
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Lỗi server: {str(e)}'
#         }), 500

# @auth_bp.route('/profile', methods=['GET'])
# def get_profile():
#     """API lấy thông tin profile"""
#     try:
#         if 'user_id' not in session:
#             return jsonify({
#                 'success': False,
#                 'message': 'Chưa đăng nhập'
#             }), 401
        
#         return jsonify({
#             'success': True,
#             'user': {
#                 'id': session['user_id'],
#                 'username': session['username'],
#                 'email': session['email'],
#                 'role': session['role']
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Lỗi server: {str(e)}'
#         }), 500

# @auth_bp.route('/check-session', methods=['GET'])
# def check_session():
#     """API kiểm tra session"""
#     try:
#         if 'user_id' in session:
#             return jsonify({
#                 'success': True,
#                 'logged_in': True,
#                 'user': {
#                     'id': session['user_id'],
#                     'username': session['username'],
#                     'email': session['email'],
#                     'role': session['role']
#                 }
#             }), 200
#         else:
#             return jsonify({
#                 'success': True,
#                 'logged_in': False
#             }), 200
            
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Lỗi server: {str(e)}'
#         }), 500