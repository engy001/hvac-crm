import os
import json
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

def analyze_stage(country, product, quotation_date, days_since_quotation, 
                  quotation_amount, last_message, customer_has_responded):
    """
    使用 DeepSeek API 分析客户当前阶段
    
    返回:
    {
        'current_stage': str,
        'risk_level': 'high' | 'medium' | 'low',
        'recommended_action': str,
        'urgency': 'critical' | 'high' | 'normal',
        'notes': str
    }
    """
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    if not api_key:
        return {
            'current_stage': 'unknown',
            'risk_level': 'medium',
            'recommended_action': '（API 未配置）',
            'urgency': 'normal',
            'notes': 'API 密钥未配置'
        }
    
    prompt = f"""作为 HVAC 销售顾问，分析以下客户情况，判断其当前阶段和风险级别：

国家: {country}
产品: {product}
报价日期: {quotation_date}
距离报价天数: {days_since_quotation}
报价金额: ${quotation_amount}
客户是否回复: {customer_has_responded}
最后信息: {last_message or '无'}

请分析：
1. 客户当前处于哪个阶段（价格比较/技术确认/项目启动/协商/已暂停/已失单）
2. 风险等级（高/中/低）
3. 建议的下一步行动
4. 紧急程度（紧急/高/正常）
5. 分析说明

返回格式：
{{
    "current_stage": "...",
    "risk_level": "high|medium|low",
    "recommended_action": "...",
    "urgency": "critical|high|normal",
    "notes": "..."
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
                        "content": "你是一个资深的 HVAC 项目销售顾问，擅长分析客户行为和预测成交概率。"
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
                'current_stage': 'unknown',
                'risk_level': 'medium',
                'recommended_action': '（API 错误）',
                'urgency': 'normal',
                'notes': f'API 错误: {response.status_code}'
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
                'current_stage': 'unknown',
                'risk_level': 'medium',
                'recommended_action': content,
                'urgency': 'normal',
                'notes': '无法解析 API 响应'
            }
    except Exception as e:
        return {
            'current_stage': 'unknown',
            'risk_level': 'medium',
            'recommended_action': '发生错误',
            'urgency': 'normal',
            'notes': f'错误: {str(e)}'
        }
