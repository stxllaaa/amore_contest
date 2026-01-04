"""
아모레퍼시픽 CRM 마케팅 메시지 생성 웹 애플리케이션
Vercel Serverless Function
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.message_generator import MarketingMessageAgent

app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')
CORS(app)

# 전역 에이전트 인스턴스 (재사용)
agent = None


def get_agent():
    """에이전트 싱글톤 패턴"""
    global agent
    if agent is None:
        db_path = os.path.join(root_path, "brands_db")
        agent = MarketingMessageAgent(db_path=db_path)
    return agent


@app.route('/')
def home():
    """메인 페이지"""
    static_path = os.path.join(root_path, 'static')
    return send_from_directory(static_path, 'index.html')


@app.route('/style.css')
def style():
    """CSS 파일"""
    static_path = os.path.join(root_path, 'static')
    return send_from_directory(static_path, 'style.css')


@app.route('/script.js')
def script():
    """JS 파일"""
    static_path = os.path.join(root_path, 'static')
    return send_from_directory(static_path, 'script.js')


@app.route('/api/generate', methods=['POST'])
def generate_message():
    """메시지 생성 API"""
    try:
        data = request.json

        # 폼 데이터에서 페르소나 정보 추출
        persona_data = {
            'age': data.get('age'),
            'gender': data.get('gender', '여성'),
            'price_sensitivity': data.get('price_sensitivity', 'Mid'),
            'skin_type': data.get('skin_type', '복합성'),
            'skin_concerns': data.get('skin_concerns', ''),
            'preferred_brands': data.get('preferred_brand', '라네즈'),
            'lifestyle_keywords': ', '.join(data.get('lifestyle_keywords', [])),
            'product_category': data.get('product_category', 'skin'),
        }

        message_purpose = data.get('message_purpose', 'personalized')
        brand = data.get('brand')

        # 에이전트로 메시지 생성
        agent_instance = get_agent()
        result = agent_instance.generate_message_from_data(
            persona_data=persona_data,
            message_purpose=message_purpose,
            brand=brand
        )

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/brands', methods=['GET'])
def get_brands():
    """브랜드 목록 반환"""
    brands = [
        {'id': 'etude', 'name': '에뛰드', 'description': '발랄하고 트렌디한 젊은 감성'},
        {'id': 'laneige', 'name': '라네즈', 'description': '친근하고 실용적인 일상 뷰티'},
        {'id': 'hera', 'name': '헤라', 'description': '세련되고 프로페셔널한 도시 여성'},
        {'id': 'sulwhasoo', 'name': '설화수', 'description': '고급스럽고 전통적인 한방 프리미엄'},
        {'id': 'iope', 'name': '아이오페', 'description': '과학적이고 신뢰감 있는 더마 케어'}
    ]
    return jsonify(brands)


@app.route('/api/save', methods=['POST'])
def save_marketing_data():
    """생성된 마케팅 메시지를 CSV 파일에 저장"""
    try:
        import csv
        from datetime import datetime

        data = request.json

        # CSV 파일 경로
        csv_path = os.path.join(root_path, 'marketing_data_asset.csv')

        # 저장할 데이터
        row = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'input_keywords': data.get('input_keywords', ''),
            'original_title': data.get('original_title', ''),
            'original_body': data.get('original_body', ''),
            'final_title': data.get('final_title', ''),
            'final_body': data.get('final_body', ''),
            'is_edited': data.get('is_edited', False)
        }

        # CSV 파일이 없으면 헤더와 함께 생성
        file_exists = os.path.exists(csv_path)

        with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['timestamp', 'input_keywords', 'original_title', 'original_body', 'final_title', 'final_body', 'is_edited']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        return jsonify({
            'success': True,
            'message': '마케팅 자산으로 저장되었습니다.'
        })

    except Exception as e:
        print(f"Save Error: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Vercel Serverless Function 핸들러
if __name__ != '__main__':
    # Vercel에서 실행될 때
    handler = app
else:
    # 로컬에서 실행될 때
    if __name__ == '__main__':
        app.run(debug=True, port=5000)
