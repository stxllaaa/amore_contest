"""
전체 조합 테스트 스크립트
모든 페르소나 × 모든 메시지 목적 조합으로 메시지 생성 및 평가
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.message_generator import MarketingMessageAgent
from evaluation.evaluator import MessageEvaluator


class ComprehensiveTester:
    """전체 조합 테스트 클래스"""

    def __init__(self, db_path: str = "./brands_db"):
        self.db_path = db_path
        self.agent = None
        self.evaluator = MessageEvaluator()

        # 페르소나 목록 (테스트용: 2명만)
        self.personas = [
            "persona_001",  # 트렌디 대학생 지민
            "persona_002"   # 실용적 직장인 수연
        ]

        # 전체 테스트용 (8명)
        # self.personas = [
        #     f"persona_{str(i).zfill(3)}" for i in range(1, 9)
        # ]

        # 메시지 목적 (5가지)
        self.message_purposes = [
            "new_product",
            "repurchase",
            "promotion",
            "seasonal",
            "personalized"
        ]

        # 결과 저장 디렉토리
        self.results_dir = Path("evaluation/results")
        self.results_dir.mkdir(exist_ok=True, parents=True)

    def run_full_test(self) -> pd.DataFrame:
        """전체 조합 테스트 실행"""

        print("\n" + "="*60)
        print("전체 조합 테스트 시작")
        print(f"페르소나: {len(self.personas)}명")
        print(f"메시지 목적: {len(self.message_purposes)}가지")
        print(f"총 조합: {len(self.personas) * len(self.message_purposes)}개")
        print("="*60)

        # 에이전트 초기화 (한 번만)
        print("\n[초기화] 에이전트 및 벡터 스토어 로딩...")
        start_init = time.time()
        self.agent = MarketingMessageAgent(db_path=self.db_path)
        init_time = time.time() - start_init
        print(f"[초기화 완료] {init_time:.2f}초")

        # 페르소나 데이터 로드
        personas_df = pd.read_csv(
            Path(os.getenv("CUSTOMERS_DB_PATH", "./customers_db")) / "customer_personas.csv",
            encoding='utf-8-sig'
        )

        # 결과 저장 리스트
        results = []

        # 전체 조합 테스트
        total_combinations = len(self.personas) * len(self.message_purposes)
        current = 0

        # CSV 파일 경로 미리 설정
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.results_dir / f"test_results_{timestamp}.csv"

        for persona_id in self.personas:
            # 페르소나 정보 가져오기
            persona_row = personas_df[personas_df['persona_id'] == persona_id]
            if persona_row.empty:
                print(f"[WARNING] {persona_id} 정보를 찾을 수 없습니다.")
                continue

            persona_info = persona_row.iloc[0].to_dict()

            for purpose in self.message_purposes:
                current += 1

                print(f"\n[{current}/{total_combinations}] {persona_id} × {purpose}")
                print("-" * 60)

                # 메시지 생성 및 시간 측정
                start_time = time.time()

                try:
                    result = self.agent.generate_message(
                        persona_id=persona_id,
                        message_purpose=purpose
                    )

                    generation_time = time.time() - start_time

                    # 평가 실행
                    eval_start = time.time()
                    evaluation = self.evaluator.evaluate_message(
                        title=result['title'],
                        body=result['body'],
                        brand=self._get_brand_id(result['brand']),
                        persona_info=persona_info,
                        message_purpose=purpose
                    )
                    eval_time = time.time() - eval_start

                    # 결과 저장
                    result_row = {
                        # 기본 정보
                        'timestamp': datetime.now().isoformat(),
                        'persona_id': persona_id,
                        'persona_name': persona_info.get('persona_name', ''),
                        'age': persona_info.get('age', ''),
                        'gender': persona_info.get('gender', ''),
                        'occupation': persona_info.get('occupation', ''),
                        'message_purpose': purpose,
                        'brand': result['brand'],

                        # 생성된 메시지
                        'title': result['title'],
                        'title_length': len(result['title']),
                        'body': result['body'],
                        'body_length': len(result['body']),
                        'products': ', '.join(result['products']),

                        # 평가 점수
                        'score_brand_tone': evaluation['scores']['brand_tone'],
                        'score_persona_fit': evaluation['scores']['persona_fit'],
                        'score_naturalness': evaluation['scores']['naturalness'],
                        'score_purchase_motivation': evaluation['scores']['purchase_motivation'],
                        'score_overall': evaluation['scores']['overall'],

                        # 제약 조건
                        'constraint_title_valid': evaluation['constraints_check']['title_valid'],
                        'constraint_body_valid': evaluation['constraints_check']['body_valid'],
                        'constraint_forbidden_valid': evaluation['constraints_check']['forbidden_words_valid'],
                        'constraints_all_met': evaluation['constraints_check']['all_constraints_met'],

                        # 톤 분석
                        'tone_consistency': evaluation['tone_analysis']['tone_consistency_score'],
                        'tone_endings_found': ', '.join(evaluation['tone_analysis']['expected_endings_found']),
                        'tone_words_found': ', '.join(evaluation['tone_analysis']['expected_words_found']),

                        # 시간 측정
                        'generation_time_sec': round(generation_time, 2),
                        'evaluation_time_sec': round(eval_time, 2),

                        # 피드백 및 상태
                        'feedback': evaluation['feedback'],
                        'is_valid': result['is_valid'],
                        'error': None
                    }

                    results.append(result_row)

                    # 진행 상황 출력
                    print(f"  [SUCCESS] 제목: {result['title'][:40]}...")
                    print(f"  [SUCCESS] 전체 점수: {evaluation['scores']['overall']:.2f}/5.0")
                    print(f"  [SUCCESS] 생성 시간: {generation_time:.2f}초")
                    print(f"  [SUCCESS] 제약 조건: {'통과' if result_row['constraints_all_met'] else '실패'}")

                except Exception as e:
                    generation_time = time.time() - start_time

                    # 에러 발생 시에도 기본 정보 저장
                    error_row = {
                        'timestamp': datetime.now().isoformat(),
                        'persona_id': persona_id,
                        'persona_name': persona_info.get('persona_name', ''),
                        'age': persona_info.get('age', ''),
                        'gender': persona_info.get('gender', ''),
                        'occupation': persona_info.get('occupation', ''),
                        'message_purpose': purpose,
                        'brand': None,
                        'title': None,
                        'title_length': 0,
                        'body': None,
                        'body_length': 0,
                        'products': None,
                        'score_brand_tone': 0,
                        'score_persona_fit': 0,
                        'score_naturalness': 0,
                        'score_purchase_motivation': 0,
                        'score_overall': 0,
                        'constraint_title_valid': False,
                        'constraint_body_valid': False,
                        'constraint_forbidden_valid': False,
                        'constraints_all_met': False,
                        'tone_consistency': 0,
                        'tone_endings_found': '',
                        'tone_words_found': '',
                        'generation_time_sec': round(generation_time, 2),
                        'evaluation_time_sec': 0,
                        'feedback': '',
                        'is_valid': False,
                        'error': str(e)
                    }
                    results.append(error_row)

                    print(f"  [ERROR] 생성 실패: {e}")
                    import traceback
                    traceback.print_exc()

                # 중간 저장 (5개마다)
                if current % 5 == 0 and results:
                    df_temp = pd.DataFrame(results)
                    df_temp.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    print(f"\n  [중간 저장] {len(results)}개 결과 저장됨 → {csv_path}")

        # 최종 저장
        if results:
            df = pd.DataFrame(results)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')

            print("\n" + "="*60)
            print("전체 테스트 완료!")
            print(f"총 {len(results)}개 메시지 생성 및 평가 완료")
            print(f"성공: {len([r for r in results if r['error'] is None])}개")
            print(f"실패: {len([r for r in results if r['error'] is not None])}개")
            print(f"결과 저장: {csv_path}")
            print("="*60)
        else:
            df = pd.DataFrame()
            print("\n" + "="*60)
            print("[경고] 저장할 결과가 없습니다.")
            print("모든 조합에서 에러가 발생했거나 페르소나를 찾을 수 없습니다.")
            print("="*60)

        return df

    def _get_brand_id(self, brand_name: str) -> str:
        """브랜드 한글명 → 영문 ID 변환"""
        brand_map = {
            "에뛰드": "etude",
            "라네즈": "laneige",
            "헤라": "hera",
            "설화수": "sulwhasoo",
            "아이오페": "iope"
        }
        return brand_map.get(brand_name, brand_name.lower())

    def print_summary(self, df: pd.DataFrame):
        """결과 요약 출력"""

        print("\n" + "="*60)
        print("테스트 결과 요약")
        print("="*60)

        # 기본 통계
        print(f"\n[전체 통계]")
        print(f"  총 생성 메시지: {len(df)}개")
        print(f"  평균 생성 시간: {df['generation_time_sec'].mean():.2f}초")
        print(f"  평균 평가 시간: {df['evaluation_time_sec'].mean():.2f}초")

        # 점수 통계
        print(f"\n[평가 점수 평균]")
        print(f"  브랜드 톤 적합성: {df['score_brand_tone'].mean():.2f}/5.0")
        print(f"  페르소나 적합성: {df['score_persona_fit'].mean():.2f}/5.0")
        print(f"  자연스러움: {df['score_naturalness'].mean():.2f}/5.0")
        print(f"  구매 유도력: {df['score_purchase_motivation'].mean():.2f}/5.0")
        print(f"  종합 점수: {df['score_overall'].mean():.2f}/5.0")

        # 제약 조건 통과율
        print(f"\n[제약 조건 통과율]")
        print(f"  제목 길이: {df['constraint_title_valid'].sum() / len(df) * 100:.1f}%")
        print(f"  본문 길이: {df['constraint_body_valid'].sum() / len(df) * 100:.1f}%")
        print(f"  금칙어 없음: {df['constraint_forbidden_valid'].sum() / len(df) * 100:.1f}%")
        print(f"  전체 통과: {df['constraints_all_met'].sum() / len(df) * 100:.1f}%")

        # 브랜드별 통계
        print(f"\n[브랜드별 평균 점수]")
        brand_stats = df.groupby('brand')['score_overall'].agg(['mean', 'count'])
        for brand, row in brand_stats.iterrows():
            print(f"  {brand}: {row['mean']:.2f}/5.0 ({int(row['count'])}개)")

        # 메시지 목적별 통계
        print(f"\n[메시지 목적별 평균 점수]")
        purpose_stats = df.groupby('message_purpose')['score_overall'].agg(['mean', 'count'])
        for purpose, row in purpose_stats.iterrows():
            print(f"  {purpose}: {row['mean']:.2f}/5.0 ({int(row['count'])}개)")

        # 톤 일관성 통계
        print(f"\n[톤 일관성]")
        print(f"  평균 톤 일관성: {df['tone_consistency'].mean():.2%}")
        print(f"  높은 일관성(>0.5): {(df['tone_consistency'] > 0.5).sum()}개 ({(df['tone_consistency'] > 0.5).sum() / len(df) * 100:.1f}%)")

        print("="*60)


def main():
    """메인 실행 함수"""

    tester = ComprehensiveTester(db_path="./brands_db")

    # 전체 테스트 실행
    df = tester.run_full_test()

    # 요약 출력
    tester.print_summary(df)

    print("\n시각화를 보려면 다음 명령을 실행하세요:")
    print("  python evaluation/visualize_results.py")


if __name__ == "__main__":
    main()
