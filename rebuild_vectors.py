"""
벡터 스토어 재구축 스크립트
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수 확인
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY가 설정되지 않았습니다.")
    print("Please set GOOGLE_API_KEY in .env file")
    exit(1)

print(f"GOOGLE_API_KEY: {'*' * 20}{os.getenv('GOOGLE_API_KEY')[-5:]}")
print("벡터 스토어 재구축을 시작합니다...")

from src.embeddings import VectorStoreManager

# 벡터 스토어 매니저 초기화
vm = VectorStoreManager()

# 모든 벡터 스토어 구축
vm.build_all_stores()

print("\n✅ 벡터 스토어 재구축 완료!")
