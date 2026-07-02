from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Customer, FollowUp, db
from ai.customer_identifier import identify_customer
from ai.followup_generator import generate_followup_messages
from ai.stage_analyzer import analyze_stage

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/identify-customer', methods=['POST'])
@jwt_required()
def identify_customer_endpoint():
    """AI 客户身份识别"""
    data = request.get_json()
    
    result = identify_customer(
        company_description=data.get('company_description'),
        company_type=data.get('company_type'),
        industry=data.get('industry'),
        country=data.get('country'),
        email=data.get('email')
    )
    
    return jsonify(result), 200

@ai_bp.route('/generate-followup', methods=['POST'])
@jwt_required()
def generate_followup_endpoint():
    """生成跟进话术和计划"""
    data = request.get_json()
    
    # 获取客户信息
    customer_id = data.get('customer_id')
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    # 生成跟进内容
    result = generate_followup_messages(
        country=customer.country,
        product=data.get('product'),
        stage=data.get('stage'),
        customer_type=customer.company_type,
        previous_message=data.get('previous_message')
    )
    
    # 如果请求自动创建跟进计划
    if data.get('create_schedule'):
        from datetime import datetime, timedelta
        days_ahead = data.get('days_ahead', 7)
        scheduled_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        follow_up = FollowUp(
            customer_id=customer_id,
            scheduled_date=scheduled_date,
            purpose=data.get('purpose', '跟进报价'),
            suggested_message=result.get('whatsapp_message')
        )
        db.session.add(follow_up)
        db.session.commit()
        
        result['follow_up_id'] = follow_up.id
    
    return jsonify(result), 200

@ai_bp.route('/analyze-stage', methods=['POST'])
@jwt_required()
def analyze_stage_endpoint():
    """分析客户当前阶段"""
    data = request.get_json()
    
    customer_id = data.get('customer_id')
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    result = analyze_stage(
        country=customer.country,
        product=data.get('product'),
        quotation_date=data.get('quotation_date'),
        days_since_quotation=data.get('days_since_quotation'),
        quotation_amount=data.get('quotation_amount'),
        last_message=data.get('last_message'),
        customer_has_responded=data.get('customer_has_responded', False)
    )
    
    return jsonify(result), 200

@ai_bp.route('/generate-30day-plan', methods=['POST'])
@jwt_required()
def generate_30day_plan():
    """生成 30 天跟进计划"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    customer_id = data.get('customer_id')
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({'error': '客户不存在'}), 404
    
    # 删除旧的计划
    FollowUp.query.filter_by(customer_id=customer_id).delete()
    
    # 生成 30 天计划（第 3 天、第 7 天、第 14 天、第 21 天、第 28 天）
    from datetime import datetime, timedelta
    days = [3, 7, 14, 21, 28]
    
    for day in days:
        scheduled_date = datetime.utcnow() + timedelta(days=day)
        
        # 根据第几天生成不同的目的
        if day == 3:
            purpose = '初步跟进，确认客户是否收到报价'
            stage = 'price_comparison'
        elif day == 7:
            purpose = '确认客户对产品的兴趣，解答技术问题'
            stage = 'technical_confirmation'
        elif day == 14:
            purpose = '推动项目进展，确认预算和时间表'
            stage = 'project_initiation'
        elif day == 21:
            purpose = '最后跟进，确认是否需要修改报价'
            stage = 'negotiation'
        else:  # day == 28
            purpose = '总结跟进，讨论后续合作机会'
            stage = 'final_push'
        
        # 生成 AI 话术
        message_result = generate_followup_messages(
            country=customer.country,
            product=data.get('product'),
            stage=stage,
            customer_type=customer.company_type
        )
        
        follow_up = FollowUp(
            customer_id=customer_id,
            scheduled_date=scheduled_date,
            purpose=purpose,
            suggested_message=message_result.get('whatsapp_message')
        )
        db.session.add(follow_up)
    
    db.session.commit()
    
    follow_ups = FollowUp.query.filter_by(customer_id=customer_id).all()
    
    return jsonify({
        'message': '30 天计划已生成',
        'plan': [f.to_dict() for f in follow_ups]
    }), 201
