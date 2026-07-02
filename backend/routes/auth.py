from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime
from models import db, User, AuditLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '该邮箱已注册'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '该用户名已存在'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'sales'),  # 默认销售角色
        department=data.get('department')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': '缺少邮箱或密码'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': '邮箱或密码错误'}), 401
    
    if not user.is_active:
        return jsonify({'error': '账户已禁用'}), 403
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 创建 JWT token
    access_token = create_access_token(identity=user.id)
    
    # 记录审计日志
    log = AuditLog(
        user_id=user.id,
        action='login',
        resource_type='user',
        resource_id=user.id,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    # 只允许更新这些字段
    if 'username' in data:
        # 检查用户名是否已被使用
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': '该用户名已被使用'}), 400
        user.username = data['username']
    
    if 'department' in data:
        user.department = data['department']
    
    db.session.commit()
    
    return jsonify({
        'message': '更新成功',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    if not user.check_password(data['old_password']):
        return jsonify({'error': '原密码错误'}), 401
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200

# 管理员操作

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """列出所有用户（仅管理员）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

@auth_bp.route('/users/<user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """更新用户角色（仅管理员）"""
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    
    if admin.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    if 'role' not in data:
        return jsonify({'error': '缺少 role 字段'}), 400
    
    target_user.role = data['role']
    db.session.commit()
    
    # 记录审计日志
    log = AuditLog(
        user_id=admin_id,
        action='update',
        resource_type='user',
        resource_id=user_id,
        changes={'role': data['role']}
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '角色更新成功',
        'user': target_user.to_dict()
    }), 200

@auth_bp.route('/users/<user_id>/status', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    """启用/禁用用户（仅管理员）"""
    admin_id = get_jwt_identity()
    admin = User.query.get(admin_id)
    
    if admin.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': '用户不存在'}), 404
    
    data = request.get_json()
    if 'is_active' not in data:
        return jsonify({'error': '缺少 is_active 字段'}), 400
    
    target_user.is_active = data['is_active']
    db.session.commit()
    
    return jsonify({
        'message': '状态更新成功',
        'user': target_user.to_dict()
    }), 200
