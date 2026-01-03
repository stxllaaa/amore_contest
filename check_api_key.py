#!/usr/bin/env python3
"""API Key 설정 확인 스크립트"""

import os
from pathlib import Path

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ .env 파일 로드 성공")
except ImportError:
    print("⚠️  python-dotenv 설치 필요: pip install python-dotenv")
    exit(1)

# API Key 확인
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("❌ GOOGLE_API_KEY가 설정되지 않았습니다!")
    print("\n해결 방법:")
    print("1. .env 파일을 열어서")
    print("2. GOOGLE_API_KEY=여기에_실제_API키_입력")
    print("3. 저장 후 다시 실행")
    exit(1)

if api_key == 'your_google_api_key_here' or api_key == '여기에_실제_API키를_붙여넣으세요':
    print("❌ GOOGLE_API_KEY가 기본값으로 되어 있습니다!")
    print("\n실제 API Key를 입력하세요:")
    print("1. https://aistudio.google.com/app/apikey 접속")
    print("2. API Key 발급")
    print("3. .env 파일에 입력")
    exit(1)

# API Key 형식 확인 (대략적으로)
if len(api_key) < 20:
    print("⚠️  API Key가 너무 짧습니다. 올바른 키인지 확인하세요.")
    exit(1)

print(f"✅ API Key 설정 완료!")
print(f"   키 길이: {len(api_key)} 문자")
print(f"   시작 부분: {api_key[:10]}...")
print("\n다음 단계:")
print("  python build_vector.py  # 벡터 스토어 빌드")
