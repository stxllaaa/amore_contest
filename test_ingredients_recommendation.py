"""
성분 추천 프로세스 테스트 스크립트
터미널에서 성분이 어떻게 추천되는지 확인
"""

from src.message_generator import MarketingMessageAgent

print("="*60)
print("성분 추천 프로세스 테스트")
print("="*60)

# 에이전트 초기화
agent = MarketingMessageAgent(db_path="./brands_db")

# 테스트 시나리오: 건조하고 주름 고민이 있는 고객
print("\n[테스트 시나리오]")
print("- 나이: 35세")
print("- 피부 타입: 건성")
print("- 피부 고민: 건조, 주름")
print("- 선호 브랜드: 라네즈")
print("-"*60)

result = agent.generate_message_from_data(
    persona_data={
        'age': 35,
        'skin_type': '건성',
        'skin_concerns': '건조, 주름',
        'preferred_brands': '라네즈',
        'occupation': '회사원',
        'lifestyle_keywords': '직장생활, 시간부족',
        'product_category': '스킨케어'
    },
    message_purpose='personalized'
)

print("\n" + "="*60)
print("최종 생성된 메시지")
print("="*60)
print(f"\n[브랜드] {result['brand']}")
print(f"\n[제목] {result['title']}")
print(f"\n[본문]\n{result['body']}")
print(f"\n[추천 제품]")
for i, product in enumerate(result['products'], 1):
    print(f"  {i}. {product}")
print("\n" + "="*60)
