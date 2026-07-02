from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Customer, Quotation, db
from utils.report_service import export_customers_excel, export_quotations_excel, export_sales_report
from datetime import datetime
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/export-customers', methods=['POST'])
@jwt_required()
def export_customers():
    """导出客户数据为 Excel"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 获取过滤参数
    filters = request.json or {}
    
    # 构建查询
    query = Customer.query
    
    if user.role == 'sales':
        query = query.filter_by(owner_id=user_id)
    
    if filters.get('country'):
        query = query.filter_by(country=filters['country'])
    
    if filters.get('status'):
        query = query.filter_by(status=filters['status'])
    
    if filters.get('grade'):
        query = query.filter_by(customer_grade=filters['grade'])
    
    customers = query.all()
    
    try:
        file_bytes = export_customers_excel(customers)
        return send_file(
            io.BytesIO(file_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'customers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@reports_bp.route('/export-quotations', methods=['POST'])
@jwt_required()
def export_quotations():
    """导出报价数据为 Excel"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    filters = request.json or {}
    
    query = Quotation.query
    
    if user.role == 'sales':
        query = query.filter_by(created_by=user_id)
    
    if filters.get('status'):
        query = query.filter_by(status=filters['status'])
    
    if filters.get('product_type'):
        query = query.filter_by(product_type=filters['product_type'])
    
    quotations = query.all()
    
    try:
        file_bytes = export_quotations_excel(quotations)
        return send_file(
            io.BytesIO(file_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'quotations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@reports_bp.route('/sales-report', methods=['GET'])
@jwt_required()
def get_sales_report():
    """获取销售报告"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # 时间范围
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        report = export_sales_report(
            user_id if user.role == 'sales' else None,
            start_date,
            end_date
        )
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': f'生成报告失败: {str(e)}'}), 500
