"""
빠른 시작 가이드 - 1분 만에 메시지 생성해보기
"""

from src.message_generator import MarketingMessageAgent

# 1. 에이전트 초기화
print("\n[1/3] 시스템 초기화 중...")
agent = MarketingMessageAgent(db_path="./brands_db")

# 2. 메시지 생성
print("\n[2/3] 마케팅 메시지 생성 중...")
result = agent.generate_message(
    persona_id="persona_001",       # 19세 여성 대학생
    message_purpose="personalized"   # 개인 맞춤 메시지
)

# 3. 결과 출력
print("\n[3/3] 생성 완료!")
agent.print_result(result)

# 추가 정보
print("\n" + "="*60)
print("더 많은 예시를 보려면:")
print("  python demo.py")
print("\n테스트를 실행하려면:")
print("  python tests/test_generator.py")
print("="*60 + "\n")
