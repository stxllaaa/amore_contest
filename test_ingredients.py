"""
성분 DB 기능 테스트 스크립트
"""
import os
from dotenv import load_dotenv

load_dotenv()

from src.embeddings import VectorStoreManager
from src.message_generator import MarketingMessageAgent

def test_ingredient_search():
    """성분 검색 테스트"""
    print("=" * 60)
    print("성분 검색 기능 테스트")
    print("=" * 60)

    # Vector Manager 로드
    vm = VectorStoreManager()
    vm.load_stores()

    # 성분 검색 테스트
    queries = [
        "건조한 피부에 좋은 성분",
        "주름 개선에 도움되는 성분",
        "피지 조절 성분"
    ]

    for query in queries:
        print(f"\n쿼리: {query}")
        results = vm.search_ingredients(query, k=3)

        if results:
            for i, doc in enumerate(results, 1):
                print(f"  {i}. {doc.metadata.get('ingredient_kor')} ({doc.metadata.get('ingredient_eng')})")
                print(f"     효능: {doc.metadata.get('function')[:50]}...")
        else:
            print("  검색 결과 없음")

def test_message_generation():
    """메시지 생성 테스트 (성분 정보 포함 확인)"""
    print("\n" + "=" * 60)
    print("메시지 생성 테스트 (성분 정보 포함)")
    print("=" * 60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    persona_data = {
        'age': 27,
        'gender': 'F',
        'skin_type': '건성',
        'skin_concerns': '건조, 주름',
        'preferred_brands': '라네즈',
        'lifestyle_keywords': '추운 날씨, 쿨톤, 데일리 케어',
        'product_category': 'skin'
    }

    result = agent.generate_message_from_data(
        persona_data=persona_data,
        message_purpose='personalized',
        brand='라네즈'
    )

    print(f"\n생성된 메시지 제목: {result.get('title')}")
    print(f"\n본문:\n{result.get('body')}")
    print(f"\n추천 제품: {len(result.get('products', []))}개")

    for i, product in enumerate(result.get('products', []), 1):
        print(f"  {i}. {product}")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    # 1. 성분 검색 테스트
    test_ingredient_search()

    # 2. 메시지 생성 테스트
    test_message_generation()
