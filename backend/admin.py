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

@admin_bp.route("/cv/<cv_id>/delete", methods=["POST"])
def delete_cv(cv_id):
    """Xóa CV"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return redirect(url_for('admin.admin_cvs'))
            
        # Lấy thông tin CV trước khi xóa
        cv_info = db.cv_submissions.find_one({'_id': ObjectId(cv_id)})
        
        if not cv_info:
            flash("Không tìm thấy CV", "error")
            return redirect(url_for('admin.admin_cvs'))
            
        # Xóa file từ GridFS
        try:
            if fs_recruitment and cv_info.get('file_id'):
                fs_recruitment.delete(cv_info['file_id'])
                logging.info(f"Deleted GridFS file: {cv_info['file_id']}")
        except Exception as e:
            logging.error(f"Failed to delete GridFS file: {str(e)}")
            
        # Xóa metadata từ MongoDB
        result = db.cv_submissions.delete_one({'_id': ObjectId(cv_id)})
        
        if result.deleted_count > 0:
            flash(f"Đã xóa CV của {cv_info.get('original_filename', 'N/A')}", "success")
            logging.info(f"Deleted CV: {cv_info.get('original_filename')} - Position: {cv_info.get('position')}")
        else:
            flash("Không thể xóa CV", "error")
            
        return redirect(url_for('admin.admin_cvs'))
        
    except Exception as e:
        flash(f"Lỗi xóa CV: {str(e)}", "error")
        return redirect(url_for('admin.admin_cvs'))

@admin_bp.route("/cvs/bulk-delete", methods=["POST"])
def bulk_delete_cvs():
    """Xóa nhiều CV cùng lúc"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return redirect(url_for('admin.admin_cvs'))
            
        cv_ids = request.form.getlist('cv_ids')
        
        if not cv_ids:
            flash("Vui lòng chọn ít nhất một CV để xóa", "error")
            return redirect(url_for('admin.admin_cvs'))
            
        deleted_count = 0
        deleted_files = 0
        
        for cv_id in cv_ids:
            try:
                # Lấy thông tin CV
                cv_info = db.cv_submissions.find_one({'_id': ObjectId(cv_id)})
                
                if cv_info:
                    # Xóa file từ GridFS
                    if fs_recruitment and cv_info.get('file_id'):
                        try:
                            fs_recruitment.delete(cv_info['file_id'])
                            deleted_files += 1
                        except Exception as e:
                            logging.error(f"Failed to delete GridFS file {cv_info['file_id']}: {str(e)}")
                    
                    # Xóa metadata
                    result = db.cv_submissions.delete_one({'_id': ObjectId(cv_id)})
                    if result.deleted_count > 0:
                        deleted_count += 1
                        
            except Exception as e:
                logging.error(f"Failed to delete CV {cv_id}: {str(e)}")
                
        flash(f"Đã xóa {deleted_count} CV và {deleted_files} file", "success")
        logging.info(f"Bulk deleted {deleted_count} CVs and {deleted_files} files")
        
        return redirect(url_for('admin.admin_cvs'))
        
    except Exception as e:
        flash(f"Lỗi xóa CV hàng loạt: {str(e)}", "error")
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

@admin_bp.route("/contact/<contact_id>/delete", methods=["POST"])
def delete_contact(contact_id):
    """Xóa Contact submission"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return redirect(url_for('admin.admin_contacts'))
            
        # Lấy thông tin contact trước khi xóa
        contact_info = db.contact_submissions.find_one({'_id': ObjectId(contact_id)})
        
        if not contact_info:
            flash("Không tìm thấy contact", "error")
            return redirect(url_for('admin.admin_contacts'))
            
        # Xóa các ảnh từ GridFS
        deleted_images = 0
        if fs_contact and contact_info.get('image_ids'):
            for image_id in contact_info['image_ids']:
                try:
                    fs_contact.delete(image_id)
                    deleted_images += 1
                    logging.info(f"Deleted GridFS image: {image_id}")
                except Exception as e:
                    logging.error(f"Failed to delete GridFS image {image_id}: {str(e)}")
                    
        # Xóa contact submission từ MongoDB
        result = db.contact_submissions.delete_one({'_id': ObjectId(contact_id)})
        
        if result.deleted_count > 0:
            flash(f"Đã xóa contact của {contact_info.get('email', 'N/A')} (bao gồm {deleted_images} ảnh)", "success")
            logging.info(f"Deleted contact: {contact_info.get('email')} - {deleted_images} images deleted")
        else:
            flash("Không thể xóa contact", "error")
            
        return redirect(url_for('admin.admin_contacts'))
        
    except Exception as e:
        flash(f"Lỗi xóa contact: {str(e)}", "error")
        return redirect(url_for('admin.admin_contacts'))

@admin_bp.route("/contacts/bulk-delete", methods=["POST"])
def bulk_delete_contacts():
    """Xóa nhiều contact cùng lúc"""
    try:
        if db is None:
            flash("Lỗi kết nối database", "error")
            return redirect(url_for('admin.admin_contacts'))
            
        contact_ids = request.form.getlist('contact_ids')
        
        if not contact_ids:
            flash("Vui lòng chọn ít nhất một contact để xóa", "error")
            return redirect(url_for('admin.admin_contacts'))
            
        deleted_count = 0
        deleted_images = 0
        
        for contact_id in contact_ids:
            try:
                # Lấy thông tin contact
                contact_info = db.contact_submissions.find_one({'_id': ObjectId(contact_id)})
                
                if contact_info:
                    # Xóa ảnh từ GridFS
                    if fs_contact and contact_info.get('image_ids'):
                        for image_id in contact_info['image_ids']:
                            try:
                                fs_contact.delete(image_id)
                                deleted_images += 1
                            except Exception as e:
                                logging.error(f"Failed to delete GridFS image {image_id}: {str(e)}")
                    
                    # Xóa contact submission
                    result = db.contact_submissions.delete_one({'_id': ObjectId(contact_id)})
                    if result.deleted_count > 0:
                        deleted_count += 1
                        
            except Exception as e:
                logging.error(f"Failed to delete contact {contact_id}: {str(e)}")
                
        flash(f"Đã xóa {deleted_count} contact và {deleted_images} ảnh", "success")
        logging.info(f"Bulk deleted {deleted_count} contacts and {deleted_images} images")
        
        return redirect(url_for('admin.admin_contacts'))
        
    except Exception as e:
        flash(f"Lỗi xóa contact hàng loạt: {str(e)}", "error")
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
