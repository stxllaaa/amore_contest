"""
마케팅 메시지 생성 시스템 테스트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.message_generator import MarketingMessageAgent


def test_basic_message_generation():
    """기본 메시지 생성 테스트"""
    print("\n" + "="*60)
    print("테스트 1: 기본 메시지 생성 (persona_001)")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    result = agent.generate_message(
        persona_id="persona_001",
        message_purpose="personalized"
    )

    agent.print_result(result)

    # 검증
    assert result['title'], "제목이 생성되지 않았습니다"
    assert result['body'], "본문이 생성되지 않았습니다"
    assert len(result['products']) > 0, "추천 제품이 없습니다"
    print("[OK] 기본 메시지 생성 테스트 통과")


def test_new_product_message():
    """신상품 소개 메시지 테스트"""
    print("\n" + "="*60)
    print("테스트 2: 신상품 소개 메시지 (persona_002)")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    result = agent.generate_message(
        persona_id="persona_002",
        message_purpose="new_product"
    )

    agent.print_result(result)

    assert result['title'], "제목이 생성되지 않았습니다"
    assert len(result['title']) <= 40, f"제목이 너무 깁니다 ({len(result['title'])}자)"
    assert len(result['body']) <= 350, f"본문이 너무 깁니다 ({len(result['body'])}자)"
    print("[OK] 신상품 소개 메시지 테스트 통과")


def test_specific_brand():
    """특정 브랜드 지정 테스트"""
    print("\n" + "="*60)
    print("테스트 3: 특정 브랜드 지정 (설화수)")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    result = agent.generate_message(
        persona_id="persona_006",
        message_purpose="seasonal",
        brand="sulwhasoo"
    )

    agent.print_result(result)

    assert result['brand'] == "설화수", f"브랜드가 일치하지 않습니다: {result['brand']}"
    print("[OK] 특정 브랜드 지정 테스트 통과")


def test_male_persona():
    """남성 페르소나 테스트"""
    print("\n" + "="*60)
    print("테스트 4: 남성 고객 메시지 (persona_004)")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    result = agent.generate_message(
        persona_id="persona_004",
        message_purpose="repurchase"
    )

    agent.print_result(result)

    assert result['title'], "제목이 생성되지 않았습니다"
    print("[OK] 남성 페르소나 테스트 통과")


def test_all_message_purposes():
    """모든 메시지 목적 테스트"""
    print("\n" + "="*60)
    print("테스트 5: 모든 메시지 목적 테스트")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    purposes = ["new_product", "repurchase", "promotion", "seasonal", "personalized"]

    for purpose in purposes:
        print(f"\n[테스트] 메시지 목적: {purpose}")
        result = agent.generate_message(
            persona_id="persona_003",
            message_purpose=purpose
        )

        print(f"  - 제목: {result['title'][:30]}...")
        print(f"  - 제목 길이: {len(result['title'])}자")
        print(f"  - 본문 길이: {len(result['body'])}자")

        assert result['title'], f"{purpose} 메시지 제목 생성 실패"
        assert result['body'], f"{purpose} 메시지 본문 생성 실패"

    print("\n[OK] 모든 메시지 목적 테스트 통과")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*60)
    print("아모레퍼시픽 CRM 마케팅 메시지 생성 시스템 테스트")
    print("="*60)

    try:
        test_basic_message_generation()
        test_new_product_message()
        test_specific_brand()
        test_male_persona()
        test_all_message_purposes()

        print("\n" + "="*60)
        print("모든 테스트 통과!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
