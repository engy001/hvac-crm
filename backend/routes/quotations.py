from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models import db, Quotation, Customer, User, AuditLog, FollowUp

quotations_bp = Blueprint('quotations', __name__)

@quotations_bp.route('', methods=['GET'])
@jwt_required()
def list_quotations():
    """获取报价列表"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Quotation.query
    
    # 权限过滤
    if user.role == 'sales':
        query = query.filter_by(created_by=user_id)
    
    # 状态过滤
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # 产品过滤
    product = request.args.get('product')
    if product:
        query = query.filter_by(product_type=product)
    
    query = query.order_by(Quotation.created_at.desc())
    paginated = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'data': [q.to_dict() for q in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200

@quotations_bp.route('/<quotation_id>', methods=['GET'])
@jwt_required()
def get_quotation(quotation_id):
    """获取报价详情"""
    quotation = Quotation.query.get(quotation_id)
    
    if not quotation:
        return jsonify({'error': '报价不存在'}), 404
    
    return jsonify(quotation.to_dict()), 200

@quotations_bp.route('', methods=['POST'])
@jwt_required()
def create_quotation():
    """创建报价"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('customer_id'):
        return jsonify({'error': '缺少客户ID'}), 400
    
    # 验证客户存在
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    quotation = Quotation(
        customer_id=data['customer_id'],
        created_by=user_id,
        product_type=data.get('product_type'),
        product_description=data.get('product_description'),
        quantity=data.get('quantity'),
        unit_price=data.get('unit_price'),
        total_amount=data.get('total_amount'),
        currency=data.get('currency', 'USD'),
        validity_days=data.get('validity_days', 30),
        notes=data.get('notes')
    )
    
    db.session.add(quotation)
    db.session.commit()
    
    # 记录审计日志
    log = AuditLog(
        user_id=user_id,
        action='create',
        resource_type='quotation',
        resource_id=quotation.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '报价创建成功',
        'quotation': quotation.to_dict()
    }), 201

@quotations_bp.route('/<quotation_id>/send', methods=['POST'])
@jwt_required()
def send_quotation(quotation_id):
    """发送报价（标记为已发送）"""
    user_id = get_jwt_identity()
    quotation = Quotation.query.get(quotation_id)
    
    if not quotation:
        return jsonify({'error': '报价不存在'}), 404
    
    quotation.status = 'sent'
    quotation.sent_at = datetime.utcnow()
    quotation.expired_at = datetime.utcnow() + timedelta(days=quotation.validity_days)
    db.session.commit()
    
    return jsonify({
        'message': '报价已发送',
        'quotation': quotation.to_dict()
    }), 200

@quotations_bp.route('/<quotation_id>/status', methods=['PUT'])
@jwt_required()
def update_quotation_status(quotation_id):
    """更新报价状态"""
    user_id = get_jwt_identity()
    quotation = Quotation.query.get(quotation_id)
    
    if not quotation:
        return jsonify({'error': '报价不存在'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': '缺少 status 字段'}), 400
    
    quotation.status = new_status
    if new_status == 'accepted':
        quotation.responded_at = datetime.utcnow()
        # 更新客户状态为赢单
        quotation.customer.status = 'won'
    elif new_status == 'rejected':
        quotation.responded_at = datetime.utcnow()
        # 更新客户状态为失单
        quotation.customer.status = 'lost'
    
    db.session.commit()
    
    return jsonify({
        'message': '报价状态已更新',
        'quotation': quotation.to_dict()
    }), 200
