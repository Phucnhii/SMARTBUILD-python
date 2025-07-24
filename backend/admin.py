from flask import Blueprint, render_template, request, jsonify, make_response, flash, url_for, redirect
from connect_database import get_database
from gridfs import GridFS
from bson import ObjectId
from datetime import datetime
import logging

# Tạo Blueprint cho admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Khởi tạo database connection
try:
    db = get_database()
    fs_recruitment = GridFS(db, collection="cv_files")
    fs_contact = GridFS(db, collection="contact_images")
except Exception as e:
    logging.error(f"Admin module: MongoDB connection failed: {str(e)}")
    db = None
    fs_recruitment = None
    fs_contact = None

@admin_bp.route("/")
def admin_dashboard():
    """Trang admin dashboard"""
    return render_template("admin_dashboard.html")

@admin_bp.route("/cvs")
def admin_cvs():
    """Trang quản lý CV với giao diện HTML"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return render_template("admin_cvs.html", cvs=[], positions=[])
            
        # Lấy query parameters
        position = request.args.get('position')
        status = request.args.get('status', 'received')
        
        # Build query filter
        query_filter = {}
        if position:
            query_filter['position'] = position
        if status and status != 'all':
            query_filter['status'] = status
            
        # Lấy danh sách CV từ MongoDB
        cvs = list(db.cv_submissions.find(query_filter)
                  .sort('submitted_at', -1)
                  .limit(100))
        
        # Lấy danh sách positions để filter
        positions = db.cv_submissions.distinct('position')
        
        return render_template("admin_cvs.html", 
                             cvs=cvs, 
                             positions=positions,
                             current_position=position,
                             current_status=status)
                             
    except Exception as e:
        flash(f"Lỗi tải danh sách CV: {str(e)}", "error")
        return render_template("admin_cvs.html", cvs=[], positions=[])

@admin_bp.route("/api/cvs")
def api_admin_cvs():
    """API lấy danh sách CV (JSON)"""
    try:
        if db is None:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
            
        position = request.args.get('position')
        status = request.args.get('status', 'received')
        limit = int(request.args.get('limit', 50))
        
        query_filter = {}
        if position:
            query_filter['position'] = position
        if status and status != 'all':
            query_filter['status'] = status
            
        cvs = list(db.cv_submissions.find(query_filter)
                  .sort('submitted_at', -1)
                  .limit(limit))
        
        # Convert ObjectId thành string
        for cv in cvs:
            cv['_id'] = str(cv['_id'])
            cv['file_id'] = str(cv['file_id'])
            cv['submitted_at'] = cv['submitted_at'].isoformat()
            
        return jsonify({
            'status': 'success',
            'count': len(cvs),
            'data': cvs
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route("/cv/<cv_id>/status", methods=["POST"])
def update_cv_status(cv_id):
    """Cập nhật trạng thái CV"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return redirect(url_for('admin.admin_cvs'))
            
        new_status = request.form.get('status')
        
        if new_status not in ['received', 'reviewed', 'shortlisted', 'rejected']:
            flash("Trạng thái không hợp lệ", "error")
            return redirect(url_for('admin.admin_cvs'))
            
        result = db.cv_submissions.update_one(
            {'_id': ObjectId(cv_id)},
            {
                '$set': {
                    'status': new_status,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            flash(f"Đã cập nhật trạng thái thành {new_status}", "success")
        else:
            flash("Không tìm thấy CV hoặc trạng thái không thay đổi", "error")
            
        return redirect(url_for('admin.admin_cvs'))
        
    except Exception as e:
        flash(f"Lỗi cập nhật trạng thái: {str(e)}", "error")
        return redirect(url_for('admin.admin_cvs'))

@admin_bp.route("/contacts")
def admin_contacts():
    """Trang quản lý Contact Submissions"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return render_template("admin_contacts.html", contacts=[], statuses=[])
            
        # Lấy query parameters
        status = request.args.get('status', 'pending')
        
        # Build query filter
        query_filter = {}
        if status and status != 'all':
            query_filter['status'] = status
            
        # Lấy danh sách Contact từ MongoDB
        contacts = list(db.contact_submissions.find(query_filter)
                       .sort('submitted_at', -1)
                       .limit(100))
        
        # Lấy danh sách statuses để filter
        statuses = db.contact_submissions.distinct('status')
        
        return render_template("admin_contacts.html", 
                             contacts=contacts, 
                             statuses=statuses,
                             current_status=status)
                             
    except Exception as e:
        flash(f"Lỗi tải danh sách contact: {str(e)}", "error")
        return render_template("admin_contacts.html", contacts=[], statuses=[])

@admin_bp.route("/contact/<contact_id>/status", methods=["POST"])
def update_contact_status(contact_id):
    """Cập nhật trạng thái Contact"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return redirect(url_for('admin.admin_contacts'))
            
        new_status = request.form.get('status')
        
        if new_status not in ['pending', 'processing', 'completed', 'rejected']:
            flash("Trạng thái không hợp lệ", "error")
            return redirect(url_for('admin.admin_contacts'))
            
        result = db.contact_submissions.update_one(
            {'_id': ObjectId(contact_id)},
            {
                '$set': {
                    'status': new_status,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            flash(f"Đã cập nhật trạng thái thành {new_status}", "success")
        else:
            flash("Không tìm thấy contact hoặc trạng thái không thay đổi", "error")
            
        return redirect(url_for('admin.admin_contacts'))
        
    except Exception as e:
        flash(f"Lỗi cập nhật trạng thái: {str(e)}", "error")
        return redirect(url_for('admin.admin_contacts'))

@admin_bp.route("/stats")
def admin_stats():
    """Trang thống kê"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return render_template("admin_stats.html",
                                 total_cvs=0,
                                 total_contacts=0,
                                 cv_stats=[],
                                 status_stats=[])
        
        # Thống kê tổng quan
        total_cvs = db.cv_submissions.count_documents({})
        total_contacts = db.contact_submissions.count_documents({})
        
        # Thống kê CV theo position
        cv_stats = list(db.cv_submissions.aggregate([
            {
                '$group': {
                    '_id': '$position',
                    'count': {'$sum': 1}
                }
            }
        ]))
        
        # Thống kê CV theo status
        status_stats = list(db.cv_submissions.aggregate([
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }
            }
        ]))
        
        # Thống kê Contact theo status
        contact_stats = list(db.contact_submissions.aggregate([
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }
            }
        ]))
        
        return render_template("admin_stats.html",
                             total_cvs=total_cvs,
                             total_contacts=total_contacts,
                             cv_stats=cv_stats,
                             status_stats=status_stats,
                             contact_stats=contact_stats)
                             
    except Exception as e:
        flash(f"Lỗi tải thống kê: {str(e)}", "error")
        return render_template("admin_stats.html",
                             total_cvs=0,
                             total_contacts=0,
                             cv_stats=[],
                             status_stats=[],
                             contact_stats=[])

# Route download CV (không có prefix vì cần accessible từ ngoài)
def setup_download_routes(app):
    """Setup download routes cho main app"""
    
    @app.route("/download/cv/<file_id>")
    def download_cv(file_id):
        """Download file CV bằng file_id"""
        try:
            if fs_recruitment is None or db is None:
                flash("Lỗi kết nối database", "error")
                return redirect(url_for('admin.admin_cvs'))
                
            # Chuyển string thành ObjectId
            object_id = ObjectId(file_id)
            
            # Lấy file từ GridFS sử dụng fs_recruitment
            grid_out = fs_recruitment.get(object_id)
            
            # Lấy thông tin metadata
            cv_info = db.cv_submissions.find_one({'file_id': object_id})
            
            if not cv_info:
                flash("File không tìm thấy", "error")
                return redirect(url_for('admin.admin_cvs'))
                
            # Tạo response với file content
            file_data = grid_out.read()
            
            response = make_response(file_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{cv_info["original_filename"]}"'
            response.headers['Content-Length'] = len(file_data)
            
            # Log download activity
            logging.info(f"Downloaded CV: {cv_info['original_filename']} for position: {cv_info['position']}")
            
            return response
            
        except Exception as e:
            logging.error(f"Error downloading file {file_id}: {str(e)}")
            flash(f"Lỗi download file: {str(e)}", "error")
            return redirect(url_for('admin.admin_cvs'))
    
    @app.route("/download/contact/image/<file_id>")
    def download_contact_image(file_id):
        """Download ảnh contact bằng file_id"""
        try:
            if fs_contact is None or db is None:
                flash("Lỗi kết nối database", "error")
                return redirect(url_for('admin.admin_contacts'))
                
            # Chuyển string thành ObjectId
            object_id = ObjectId(file_id)
            
            # Lấy file từ GridFS sử dụng fs_contact
            grid_out = fs_contact.get(object_id)
            
            # Tạo response với file content
            file_data = grid_out.read()
            
            response = make_response(file_data)
            response.headers['Content-Type'] = grid_out.content_type or 'image/jpeg'
            response.headers['Content-Disposition'] = f'attachment; filename="{grid_out.filename}"'
            response.headers['Content-Length'] = len(file_data)
            
            # Log download activity
            logging.info(f"Downloaded contact image: {grid_out.filename}")
            
            return response
            
        except Exception as e:
            logging.error(f"Error downloading contact image {file_id}: {str(e)}")
            flash(f"Lỗi download ảnh: {str(e)}", "error")
            return redirect(url_for('admin.admin_contacts'))
