from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from models import db, Customer, Quotation, User, Interaction

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """获取销售看板摘要"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 权限检查
    if user.role == 'sales':
        customer_query = Customer.query.filter_by(owner_id=user_id)
    else:
        customer_query = Customer.query
    
    # 基础统计
    total_customers = customer_query.count()
    new_customers = customer_query.filter(
        Customer.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # 按状态统计
    status_stats = db.session.query(
        Customer.status,
        func.count(Customer.id).label('count')
    ).filter(Customer.owner_id == user_id if user.role == 'sales' else True).group_by(Customer.status).all()
    
    # 按等级统计
    grade_stats = db.session.query(
        Customer.customer_grade,
        func.count(Customer.id).label('count')
    ).filter(Customer.owner_id == user_id if user.role == 'sales' else True).group_by(Customer.customer_grade).all()
    
    # 报价统计
    quotation_query = Quotation.query
    if user.role == 'sales':
        quotation_query = quotation_query.filter_by(created_by=user_id)
    
    total_quotations = quotation_query.count()
    total_quotation_amount = db.session.query(
        func.sum(Quotation.total_amount)
    ).filter(
        Quotation.created_by == user_id if user.role == 'sales' else True
    ).scalar() or 0
    
    accepted_quotations = quotation_query.filter_by(status='accepted').count()
    
    return jsonify({
        'total_customers': total_customers,
        'new_customers_30days': new_customers,
        'total_quotations': total_quotations,
        'total_quotation_amount': float(total_quotation_amount),
        'accepted_quotations': accepted_quotations,
        'conversion_rate': round(accepted_quotations / total_quotations * 100, 2) if total_quotations > 0 else 0,
        'status_distribution': [
            {'status': s[0] or '未分类', 'count': s[1]} for s in status_stats
        ],
        'grade_distribution': [
            {'grade': g[0] or '未评级', 'count': g[1]} for g in grade_stats
        ]
    }), 200

@dashboard_bp.route('/countries', methods=['GET'])
@jwt_required()
def get_countries_distribution():
    """获取国家分布（Top 10）"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    query = db.session.query(
        Customer.country,
        func.count(Customer.id).label('count')
    )
    
    if user.role == 'sales':
        query = query.filter(Customer.owner_id == user_id)
    
    results = query.group_by(Customer.country)\
        .order_by(func.count(Customer.id).desc())\
        .limit(10).all()
    
    return jsonify([
        {'country': r[0] or '未指定', 'count': r[1]} for r in results
    ]), 200

@dashboard_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products_distribution():
    """获取产品热度排行"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    query = db.session.query(
        Quotation.product_type,
        func.count(Quotation.id).label('count'),
        func.sum(Quotation.total_amount).label('total_amount')
    )
    
    if user.role == 'sales':
        query = query.filter(Quotation.created_by == user_id)
    
    results = query.group_by(Quotation.product_type)\
        .order_by(func.count(Quotation.id).desc())\
        .all()
    
    return jsonify([
        {
            'product': r[0] or '未指定',
            'count': r[1],
            'total_amount': float(r[2]) if r[2] else 0
        } for r in results
    ]), 200

@dashboard_bp.route('/funnel', methods=['GET'])
@jwt_required()
def get_sales_funnel():
    """获取销售漏斗"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    query = Customer.query
    if user.role == 'sales':
        query = query.filter_by(owner_id=user_id)
    
    stages = [
        ('new', '新客户'),
        ('contacted', '已联系'),
        ('quoted', '已报价'),
        ('negotiating', '协商中'),
        ('won', '已成交')
    ]
    
    funnel = []
    for status, label in stages:
        count = query.filter_by(status=status).count()
        funnel.append({
            'stage': label,
            'status': status,
            'count': count
        })
    
    return jsonify(funnel), 200

@dashboard_bp.route('/timeline', methods=['GET'])
@jwt_required()
def get_timeline():
    """获取最近 30 天的销售趋势"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 获取最近 30 天的数据
    results = []
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=30-i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        
        query = Customer.query.filter(
            and_(
                Customer.created_at >= date_start,
                Customer.created_at < date_end
            )
        )
        
        if user.role == 'sales':
            query = query.filter(Customer.owner_id == user_id)
        
        count = query.count()
        results.append({
            'date': date.strftime('%Y-%m-%d'),
            'new_customers': count
        })
    
    return jsonify(results), 200
