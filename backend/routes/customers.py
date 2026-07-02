from flask import Blueprint, request, jsonify
from flask_jwt_required import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_
from datetime import datetime
from models import db, Customer, User, AuditLog, Interaction
from ai.customer_identifier import identify_customer

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@jwt_required()
def list_customers():
    """获取客户列表"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 过滤
    query = Customer.query
    
    # 普通销售只能看自己的客户
    if user.role == 'sales':
        query = query.filter_by(owner_id=user.id)
    # 经理可以看部门内的客户
    elif user.role == 'manager':
        query = query.filter_by(owner_id=user.id)
    # 管理员可以看所有客户
    
    # 搜索条件
    search = request.args.get('search')
    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.country.ilike(f'%{search}%')
            )
        )
    
    # 国家过滤
    country = request.args.get('country')
    if country:
        query = query.filter_by(country=country)
    
    # 状态过滤
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # 客户等级过滤
    grade = request.args.get('grade')
    if grade:
        query = query.filter_by(customer_grade=grade)
    
    # 排序
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    if sort_order == 'desc':
        query = query.order_by(getattr(Customer, sort_by).desc())
    else:
        query = query.order_by(getattr(Customer, sort_by))
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'data': [c.to_dict() for c in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@customers_bp.route('/<customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """获取客户详情"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    return jsonify(customer.to_dict(include_relations=True)), 200

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """创建客户"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': '缺少客户名称'}), 400
    
    customer = Customer(
        name=data['name'],
        country=data.get('country'),
        city=data.get('city'),
        email=data.get('email'),
        phone=data.get('phone'),
        whatsapp=data.get('whatsapp'),
        website=data.get('website'),
        company_type=data.get('company_type'),
        industry=data.get('industry'),
        company_description=data.get('company_description'),
        owner_id=user_id,
        source=data.get('source', 'manual')
    )
    
    # AI 评估客户
    if data.get('auto_assess'):
        ai_result = identify_customer(
            company_description=customer.company_description,
            company_type=customer.company_type,
            industry=customer.industry,
            country=customer.country,
            email=customer.email
        )
        customer.ai_score = ai_result.get('score')
        customer.customer_grade = ai_result.get('grade')
        customer.ai_notes = ai_result.get('notes')
    
    db.session.add(customer)
    db.session.commit()
    
    # 记录审计日志
    log = AuditLog(
        user_id=user_id,
        action='create',
        resource_type='customer',
        resource_id=customer.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '客户创建成功',
        'customer': customer.to_dict()
    }), 201

@customers_bp.route('/<customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """更新客户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    # 权限检查：只有owner或admin可以编辑
    if customer.owner_id != user_id and user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    
    # 更新字段
    for field in ['name', 'country', 'city', 'email', 'phone', 'whatsapp', 'website',
                   'company_type', 'industry', 'company_description', 'status']:
        if field in data:
            setattr(customer, field, data[field])
    
    customer.updated_at = datetime.utcnow()
    customer.last_contact = datetime.utcnow()
    db.session.commit()
    
    # 记录审计日志
    log = AuditLog(
        user_id=user_id,
        action='update',
        resource_type='customer',
        resource_id=customer.id,
        changes=data
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '客户信息更新成功',
        'customer': customer.to_dict()
    }), 200

@customers_bp.route('/<customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """删除客户"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    # 权限检查
    if customer.owner_id != user_id and user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    
    db.session.delete(customer)
    db.session.commit()
    
    # 记录审计日志
    log = AuditLog(
        user_id=user_id,
        action='delete',
        resource_type='customer',
        resource_id=customer_id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '客户已删除'}), 200

@customers_bp.route('/<customer_id>/interactions', methods=['GET'])
@jwt_required()
def get_interactions(customer_id):
    """获取客户互动记录"""
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    interactions = Interaction.query.filter_by(customer_id=customer_id)\
        .order_by(Interaction.created_at.desc()).all()
    
    return jsonify([i.to_dict() for i in interactions]), 200

@customers_bp.route('/<customer_id>/interactions', methods=['POST'])
@jwt_required()
def add_interaction(customer_id):
    """添加互动记录"""
    user_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    data = request.get_json()
    
    interaction = Interaction(
        customer_id=customer_id,
        type=data.get('type'),
        content=data.get('content'),
        sender=data.get('sender', 'user'),
        direction=data.get('direction', 'outbound')
    )
    
    # 更新客户的 last_contact
    customer.last_contact = datetime.utcnow()
    
    db.session.add(interaction)
    db.session.commit()
    
    return jsonify({
        'message': '互动记录已添加',
        'interaction': interaction.to_dict()
    }), 201
