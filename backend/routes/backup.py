from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Backup, db
import os
from datetime import datetime
from utils.backup_service import create_backup, restore_backup

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/create', methods=['POST'])
@jwt_required()
def create_backup_endpoint():
    """创建备份"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 只有管理员可以创建备份
    if user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    backup_type = request.json.get('backup_type', 'full') if request.json else 'full'
    
    try:
        backup_result = create_backup(backup_type)
        
        # 记录备份
        backup = Backup(
            filename=backup_result['filename'],
            file_path=backup_result['file_path'],
            file_size=backup_result['file_size'],
            backup_type=backup_type,
            status='success'
        )
        db.session.add(backup)
        db.session.commit()
        
        return jsonify({
            'message': '备份创建成功',
            'backup': backup.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': f'备份失败: {str(e)}'}), 500

@backup_bp.route('/list', methods=['GET'])
@jwt_required()
def list_backups():
    """列出所有备份"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 只有管理员可以查看备份
    if user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated = Backup.query.order_by(Backup.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'data': [b.to_dict() for b in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@backup_bp.route('/<backup_id>/download', methods=['GET'])
@jwt_required()
def download_backup(backup_id):
    """下载备份文件"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    backup = Backup.query.get(backup_id)
    if not backup:
        return jsonify({'error': '备份不存在'}), 404
    
    if not os.path.exists(backup.file_path):
        return jsonify({'error': '备份文件不存在'}), 404
    
    return send_file(backup.file_path, as_attachment=True, download_name=backup.filename)

@backup_bp.route('/<backup_id>/restore', methods=['POST'])
@jwt_required()
def restore_backup_endpoint(backup_id):
    """恢复备份"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    backup = Backup.query.get(backup_id)
    if not backup:
        return jsonify({'error': '备份不存在'}), 404
    
    try:
        restore_backup(backup.file_path)
        return jsonify({'message': '备份已恢复'}), 200
    except Exception as e:
        return jsonify({'error': f'恢复失败: {str(e)}'}), 500
