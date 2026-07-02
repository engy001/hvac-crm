import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

def generate_followup_messages(country, product, stage, customer_type=None, previous_message=None):
    """
    使用 DeepSeek API 生成本地化跟进话术
    
    返回:
    {
        'whatsapp_message': str,
        'email_subject': str,
        'email_message': str,
        'call_talking_points': list
    }
    """
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    if not api_key:
        return {
            'whatsapp_message': '（API 未配置）',
            'email_subject': '（API 未配置）',
            'email_message': '（API 未配置）',
            'call_talking_points': []
        }
    
    # 阶段和国家对应的文化提示
    stage_desc = {
        'price_comparison': '客户正在比较价格',
        'technical_confirmation': '客户需要技术确认',
        'project_initiation': '项目启动阶段',
        'negotiation': '协商阶段',
        'final_push': '最后冲刺'
    }
    
    prompt = f"""作为资深的 HVAC 外贸销售，为 {country} 的客户生成跟进话术。

客户信息：
- 国家：{country}
- 产品：{product}
- 当前阶段：{stage_desc.get(stage, stage)}
- 客户类型：{customer_type or '未知'}
- 之前的信息：{previous_message or '无'}

请考虑该国的商务文化、语言习惯和时区。生成以下内容：

1. WhatsApp 消息（简洁、友好，不要过度销售）
2. 邮件主题
3. 正式邮件内容
4. 电话沟通要点（列表形式）

返回格式：
{{
    "whatsapp_message": "...",
    "email_subject": "...",
    "email_message": "...",
    "call_talking_points": ["...", "..."]
}}"""
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个资深的 HVAC 外贸销售专家，懂得当地文化和商务礼仪，能生成高效的本地化跟进话术。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
        )
        
        if response.status_code != 200:
            return {
                'whatsapp_message': '（API 错误）',
                'email_subject': '（API 错误）',
                'email_message': '（API 错误）',
                'call_talking_points': []
            }
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # 解析 JSON
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return parsed
        else:
            return {
                'whatsapp_message': content,
                'email_subject': '跟进',
                'email_message': content,
                'call_talking_points': [content]
            }
    except Exception as e:
        return {
            'whatsapp_message': f'错误: {str(e)}',
            'email_subject': '错误',
            'email_message': f'错误: {str(e)}',
            'call_talking_points': []
        }
