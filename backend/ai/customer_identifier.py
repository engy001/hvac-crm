import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

def identify_customer(company_description, company_type, industry, country, email):
    """
    使用 DeepSeek API 识别客户身份
    
    返回:
    {
        'type': 'distributor' | 'epc' | 'end_user' | 'trader',
        'score': 0-100,
        'grade': 'A' | 'B' | 'C',
        'confidence': 0-1,
        'notes': str
    }
    """
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    if not api_key:
        return {
            'type': 'unknown',
            'score': 50,
            'grade': 'B',
            'confidence': 0,
            'notes': 'API 密钥未配置'
        }
    
    prompt = f"""作为 HVAC 行业专家，分析以下客户信息并判断客户类型：

公司描述: {company_description}
申报客户类型: {company_type}
行业: {industry}
国家: {country}
邮箱: {email}

请返回 JSON 格式的分析结果，包含：
1. type: 客户类型 (distributor/经销商, epc/工程承包商, end_user/终端客户, trader/贸易商)
2. score: 客户质量评分 0-100
3. grade: 客户等级 A/B/C (A 最好)
4. confidence: 判断置信度 0-1
5. notes: 分析说明

返回格式：
{{
    "type": "...",
    "score": ...,
    "grade": "...",
    "confidence": ...,
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
                        "content": "你是一个资深的 HVAC 行业销售专家，熟悉全球市场，特别是非洲、中东、拉美和中亚市场。"
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
                'type': 'unknown',
                'score': 50,
                'grade': 'B',
                'confidence': 0,
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
                'type': 'unknown',
                'score': 50,
                'grade': 'B',
                'confidence': 0,
                'notes': '无法解析 API 响应'
            }
    except Exception as e:
        return {
            'type': 'unknown',
            'score': 50,
            'grade': 'B',
            'confidence': 0,
            'notes': f'错误: {str(e)}'
        }
