"""
샘플 평가 스크립트 - 빠른 테스트용
1-2개 메시지만 생성하고 평가하여 시스템 동작 확인
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.message_generator import MarketingMessageAgent
from evaluation.evaluator import MessageEvaluator
import pandas as pd


def sample_evaluation():
    """샘플 평가 실행"""

    print("\n" + "="*60)
    print("샘플 평가 - 빠른 시스템 동작 확인")
    print("="*60)

    # 에이전트 및 평가기 초기화
    print("\n[1/4] 시스템 초기화 중...")
    agent = MarketingMessageAgent(db_path="./brands_db")
    evaluator = MessageEvaluator()

    # 페르소나 데이터 로드
    personas_df = pd.read_csv("./customers_db/customer_personas.csv", encoding='utf-8-sig')

    # 테스트할 샘플 조합 (2개)
    samples = [
        {
            "persona_id": "persona_001",
            "message_purpose": "new_product",
            "description": "19세 여성 대학생, 신상품 소개"
        },
        {
            "persona_id": "persona_006",
            "message_purpose": "seasonal",
            "description": "48세 여성 전문직, 계절 추천"
        }
    ]

    results = []

    for idx, sample in enumerate(samples, 1):
        print(f"\n[{idx+1}/4] 샘플 {idx} 테스트: {sample['description']}")
        print("-" * 60)

        # 메시지 생성
        result = agent.generate_message(
            persona_id=sample['persona_id'],
            message_purpose=sample['message_purpose']
        )

        # 페르소나 정보 가져오기
        persona_info = personas_df[
            personas_df['persona_id'] == sample['persona_id']
        ].iloc[0].to_dict()

        # 평가 실행
        brand_id = _get_brand_id(result['brand'])
        evaluation = evaluator.evaluate_message(
            title=result['title'],
            body=result['body'],
            brand=brand_id,
            persona_info=persona_info,
            message_purpose=sample['message_purpose']
        )

        # 결과 출력
        print(f"\n[메시지]")
        print(f"  브랜드: {result['brand']}")
        print(f"  제목 ({len(result['title'])}자): {result['title']}")
        print(f"  본문 ({len(result['body'])}자): {result['body'][:80]}...")
        print(f"  추천 제품: {', '.join(result['products'][:2])}...")

        print(f"\n[평가 점수]")
        print(f"  브랜드 톤 적합성: {evaluation['scores']['brand_tone']:.1f}/5.0")
        print(f"  페르소나 적합성: {evaluation['scores']['persona_fit']:.1f}/5.0")
        print(f"  자연스러움: {evaluation['scores']['naturalness']:.1f}/5.0")
        print(f"  구매 유도력: {evaluation['scores']['purchase_motivation']:.1f}/5.0")
        print(f"  종합 점수: {evaluation['scores']['overall']:.2f}/5.0")

        print(f"\n[제약 조건]")
        print(f"  제목 길이: {'통과' if evaluation['constraints_check']['title_valid'] else '실패'}")
        print(f"  본문 길이: {'통과' if evaluation['constraints_check']['body_valid'] else '실패'}")
        print(f"  금칙어: {'없음' if evaluation['constraints_check']['forbidden_words_valid'] else '발견'}")

        print(f"\n[톤 분석]")
        print(f"  톤 일관성: {evaluation['tone_analysis']['tone_consistency_score']:.1%}")
        print(f"  발견된 어미: {', '.join(evaluation['tone_analysis']['expected_endings_found'][:3]) or '없음'}")
        print(f"  발견된 키워드: {', '.join(evaluation['tone_analysis']['expected_words_found'][:3]) or '없음'}")

        print(f"\n[피드백]")
        print(f"  {evaluation['feedback']}")

        results.append({
            'sample': sample['description'],
            'overall_score': evaluation['scores']['overall'],
            'constraints_met': evaluation['constraints_check']['all_constraints_met']
        })

    # 요약
    print(f"\n[{len(samples)+2}/4] 평가 요약")
    print("="*60)

    avg_score = sum(r['overall_score'] for r in results) / len(results)
    all_passed = all(r['constraints_met'] for r in results)

    print(f"\n평균 종합 점수: {avg_score:.2f}/5.0")
    print(f"제약 조건 통과: {len([r for r in results if r['constraints_met']])}/{len(results)}")
    print(f"\n시스템 상태: {'정상 동작' if avg_score >= 3.0 and all_passed else '개선 필요'}")

    print("\n" + "="*60)
    print("샘플 평가 완료!")
    print("="*60)

    print("\n전체 평가를 실행하려면:")
    print("  python run_evaluation.py")


def _get_brand_id(brand_name: str) -> str:
    """브랜드 한글명 → 영문 ID 변환"""
    brand_map = {
        "에뛰드": "etude",
        "라네즈": "laneige",
        "헤라": "hera",
        "설화수": "sulwhasoo",
        "아이오페": "iope"
    }
    return brand_map.get(brand_name, brand_name.lower())


if __name__ == "__main__":
    sample_evaluation()
