"""
아모레퍼시픽 CRM 마케팅 메시지 생성 시스템 데모
"""

from src.message_generator import MarketingMessageAgent


def demo_basic_usage():
    """기본 사용 예시"""
    print("\n" + "="*60)
    print("데모 1: 기본 메시지 생성")
    print("="*60)

    # 에이전트 초기화
    agent = MarketingMessageAgent(db_path="./brands_db")

    # 메시지 생성
    result = agent.generate_message(
        persona_id="persona_001",
        message_purpose="personalized"
    )

    # 결과 출력
    agent.print_result(result)


def demo_new_product():
    """신상품 소개 메시지 예시"""
    print("\n" + "="*60)
    print("데모 2: 신상품 소개 메시지")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    result = agent.generate_message(
        persona_id="persona_002",  # 26세 여성, 마케터
        message_purpose="new_product"
    )

    agent.print_result(result)


def demo_specific_brand():
    """특정 브랜드 지정 예시"""
    print("\n" + "="*60)
    print("데모 3: 설화수 브랜드 지정")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    result = agent.generate_message(
        persona_id="persona_006",  # 48세 여성, 전문직
        message_purpose="seasonal",
        brand="sulwhasoo"
    )

    agent.print_result(result)


def demo_male_customer():
    """남성 고객 메시지 예시"""
    print("\n" + "="*60)
    print("데모 4: 남성 고객 메시지")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    result = agent.generate_message(
        persona_id="persona_004",  # 35세 남성, 직장인
        message_purpose="repurchase"
    )

    agent.print_result(result)


def demo_multiple_purposes():
    """다양한 메시지 목적 예시"""
    print("\n" + "="*60)
    print("데모 5: 다양한 메시지 목적")
    print("="*60)

    agent = MarketingMessageAgent(db_path="./brands_db")

    purposes = {
        "new_product": "신상품 소개",
        "repurchase": "재구매 유도",
        "promotion": "프로모션 안내",
        "seasonal": "계절별 추천"
    }

    for purpose, desc in purposes.items():
        print(f"\n[{desc}]")
        result = agent.generate_message(
            persona_id="persona_003",
            message_purpose=purpose
        )

        print(f"제목: {result['title']}")
        print(f"본문 미리보기: {result['body'][:50]}...")
        print("-" * 60)


def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("아모레퍼시픽 CRM 마케팅 메시지 생성 시스템 - 데모")
    print("="*60)

    demos = [
        ("기본 메시지 생성", demo_basic_usage),
        ("신상품 소개 메시지", demo_new_product),
        ("설화수 브랜드 지정", demo_specific_brand),
        ("남성 고객 메시지", demo_male_customer),
        ("다양한 메시지 목적", demo_multiple_purposes)
    ]

    print("\n사용 가능한 데모:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print("0. 모든 데모 실행")

    try:
        choice = input("\n실행할 데모 번호를 선택하세요 (0-5): ").strip()

        if choice == "0":
            for name, demo_func in demos:
                demo_func()
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            demos[int(choice) - 1][1]()
        else:
            print("잘못된 선택입니다. 모든 데모를 실행합니다.")
            for name, demo_func in demos:
                demo_func()

    except KeyboardInterrupt:
        print("\n\n데모를 종료합니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
