import os
import json
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from models import db, User
from routes.auth import auth_bp
from routes.customers import customers_bp
from routes.quotations import quotations_bp
from routes.ai_agents import ai_bp
from routes.dashboard import dashboard_bp
from routes.backup import backup_bp
from routes.communications import communications_bp, init_communications
from routes.export_reports import export_reports_bp
from utils.email_service import init_mail
from utils.backup_service import init_backup_scheduler

load_dotenv()

app = Flask(__name__)

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# 邮件配置
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# 初始化扩展
db.init_app(app)
jwt = JWTManager(app)
CORS(app)
mail = Mail(app)

# 初始化服务
init_mail(app)
init_backup_scheduler(app)
init_communications(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(quotations_bp, url_prefix='/api/quotations')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(backup_bp, url_prefix='/api/backup')
app.register_blueprint(communications_bp, url_prefix='/api/communications')
app.register_blueprint(export_reports_bp, url_prefix='/api/export')

# 全局错误处理
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': '未找到该资源'}), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return jsonify({'error': '服务器内部错误'}), 500

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': '未授权'}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': '禁止访问'}), 403

# 健康检查
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'HVAC CRM 系统运行中'}), 200

# 创建数据库表
with app.app_context():
    db.create_all()
    # 创建默认管理员
    admin = User.query.filter_by(email='admin@hvac-crm.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hvac-crm.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('✓ 默认管理员已创建: admin@hvac-crm.com (密码: admin123)')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
