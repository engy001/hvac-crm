import os
from flask_mail import Mail, Message
from flask import current_app
from dotenv import load_dotenv

load_dotenv()

mail = Mail()

def init_mail(app):
    """初始化邮件服务"""
    mail.init_app(app)

def send_email(to, subject, body, html=None):
    """发送邮件"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            body=body,
            html=html
        )
        mail.send(msg)
        return True, "邮件已发送"
    except Exception as e:
        return False, f"邮件发送失败: {str(e)}"

def send_quotation_email(customer_email, quotation_data):
    """发送报价邮件"""
    subject = f"HVAC 产品报价 - {quotation_data['product_type']}"
    
    html = f"""<html>
    <body>
        <h2>亲爱的客户，</h2>
        <p>感谢您的询问。我们为您提供以下报价：</p>
        <table border="1" style="border-collapse: collapse;">
            <tr>
                <th>产品</th>
                <td>{quotation_data['product_type']}</td>
            </tr>
            <tr>
                <th>数量</th>
                <td>{quotation_data['quantity']}</td>
            </tr>
            <tr>
                <th>单价</th>
                <td>${quotation_data['unit_price']}</td>
            </tr>
            <tr>
                <th>总价</th>
                <td>${quotation_data['total_amount']}</td>
            </tr>
            <tr>
                <th>有效期</th>
                <td>{quotation_data['validity_days']} 天</td>
            </tr>
        </table>
        <p>如有任何疑问，欢迎随时联系我们。</p>
        <p>最诚挚的问候</p>
    </body>
    </html>"""
    
    return send_email(customer_email, subject, html, html)

def send_followup_email(customer_email, followup_content):
    """发送跟进邮件"""
    subject = "关于您的询问 - 我们继续为您服务"
    html = f"""<html>
    <body>
        <h2>亲爱的客户，</h2>
        <p>{followup_content}</p>
        <p>如有任何疑问，欢迎联系我们。</p>
        <p>最诚挚的问候</p>
    </body>
    </html>"""
    
    return send_email(customer_email, subject, html, html)
