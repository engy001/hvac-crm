from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='sales')  # admin, manager, sales
    department = db.Column(db.String(100))  # 部门
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    customers = db.relationship('Customer', backref='owner', lazy=True)
    quotations = db.relationship('Quotation', backref='created_by_user', lazy=True)
    logs = db.relationship('AuditLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Customer(db.Model):
    """客户模型"""
    __tablename__ = 'customers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # 客户信息
    company_type = db.Column(db.String(50))  # 经销商/EPC/终端/贸易商
    industry = db.Column(db.String(100))
    company_description = db.Column(db.Text)
    employee_count = db.Column(db.Integer)
    
    # AI 评估结果
    ai_score = db.Column(db.Integer)  # 0-100
    customer_grade = db.Column(db.String(10))  # A/B/C
    ai_notes = db.Column(db.Text)
    
    # 销售信息
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='new')  # new/contacted/quoted/negotiating/won/lost
    source = db.Column(db.String(50))  # google/linkedin/facebook/alibaba/referral
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact = db.Column(db.DateTime)
    
    # 关系
    quotations = db.relationship('Quotation', backref='customer', lazy=True, cascade='all, delete-orphan')
    interactions = db.relationship('Interaction', backref='customer', lazy=True, cascade='all, delete-orphan')
    follow_ups = db.relationship('FollowUp', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'city': self.city,
            'email': self.email,
            'phone': self.phone,
            'whatsapp': self.whatsapp,
            'website': self.website,
            'company_type': self.company_type,
            'industry': self.industry,
            'ai_score': self.ai_score,
            'customer_grade': self.customer_grade,
            'status': self.status,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'last_contact': self.last_contact.isoformat() if self.last_contact else None
        }
        if include_relations:
            data['quotations'] = [q.to_dict() for q in self.quotations]
            data['interactions'] = [i.to_dict() for i in self.interactions]
        return data

class Quotation(db.Model):
    """报价模型"""
    __tablename__ = 'quotations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # 报价详情
    product_type = db.Column(db.String(100))  # Rooftop Unit/Chiller/AHU/FCU/VRF
    product_description = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    
    # 报价状态
    status = db.Column(db.String(50), default='draft')  # draft/sent/accepted/rejected/expired
    validity_days = db.Column(db.Integer, default=30)
    notes = db.Column(db.Text)
    
    # 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    responded_at = db.Column(db.DateTime)
    expired_at = db.Column(db.DateTime)
    
    # 关系
    follow_ups = db.relationship('FollowUp', backref='quotation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'product_type': self.product_type,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'validity_days': self.validity_days
        }

class Interaction(db.Model):
    """互动记录模型"""
    __tablename__ = 'interactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    
    type = db.Column(db.String(50))  # email/whatsapp/phone/meeting/visit
    content = db.Column(db.Text)
    sender = db.Column(db.String(100))
    direction = db.Column(db.String(20))  # inbound/outbound
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'type': self.type,
            'content': self.content,
            'direction': self.direction,
            'created_at': self.created_at.isoformat()
        }

class FollowUp(db.Model):
    """跟进计划模型"""
    __tablename__ = 'follow_ups'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    quotation_id = db.Column(db.String(36), db.ForeignKey('quotations.id'))
    
    scheduled_date = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.Text)  # 跟进目的
    suggested_message = db.Column(db.Text)  # AI 建议话术
    
    status = db.Column(db.String(50), default='pending')  # pending/completed/cancelled
    actual_date = db.Column(db.DateTime)
    actual_result = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'scheduled_date': self.scheduled_date.isoformat(),
            'purpose': self.purpose,
            'status': self.status,
            'suggested_message': self.suggested_message
        }

class AuditLog(db.Model):
    """审计日志模型"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    action = db.Column(db.String(100))  # create/update/delete/login
    resource_type = db.Column(db.String(50))  # customer/quotation/user
    resource_id = db.Column(db.String(36))
    changes = db.Column(db.JSON)  # 变更内容
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'resource_type': self.resource_type,
            'changes': self.changes,
            'created_at': self.created_at.isoformat()
        }

class Backup(db.Model):
    """备份记录模型"""
    __tablename__ = 'backups'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # 字节
    backup_type = db.Column(db.String(50))  # full/incremental
    status = db.Column(db.String(50), default='success')  # success/failed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'backup_type': self.backup_type,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
