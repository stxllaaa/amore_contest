"""
마케팅 메시지 자동 생성 에이전트
사용자 인터페이스 제공
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from .embeddings import VectorStoreManager
from .graph_builder import build_message_generation_graph


class MarketingMessageAgent:
    """마케팅 메시지 생성 에이전트"""

    def __init__(self, db_path: str = "./brands_db"):
        """
        Args:
            db_path: 브랜드 데이터베이스 경로
        """
        # 환경변수 로드
        load_dotenv()

        self.db_path = db_path
        self.vector_path = os.getenv("VECTOR_STORE_PATH", "./vector_store")

        # Vector Store 초기화
        print("\n" + "="*60)
        print("아모레퍼시픽 CRM 마케팅 메시지 자동 생성 시스템")
        print("="*60)

        self.vector_manager = VectorStoreManager(db_path, self.vector_path)

        # 벡터 스토어 로드 또는 생성
        if Path(self.vector_path).exists() and \
           (Path(self.vector_path) / "products").exists():
            print("\n기존 벡터 스토어를 로드합니다...")
            self.vector_manager.load_stores()
        else:
            print("\n벡터 스토어를 새로 생성합니다...")
            self.vector_manager.build_all_stores()

        # LangGraph 구축
        print("\nLangGraph 워크플로우를 구축합니다...")
        self.graph = build_message_generation_graph(db_path, self.vector_manager)

        print("\n[OK] 시스템 초기화 완료!\n")

    def generate_message(
        self,
        persona_id: str,
        message_purpose: str = "personalized",
        brand: str = None
    ) -> dict:
        """
        마케팅 메시지 생성 (CSV 기반)

        Args:
            persona_id: 고객 페르소나 ID (예: "persona_001")
            message_purpose: 메시지 목적
                - "new_product": 신상품 소개
                - "repurchase": 재구매 유도
                - "promotion": 프로모션/할인
                - "seasonal": 계절별 추천
                - "personalized": 개인 맞춤 (기본값)
            brand: 특정 브랜드 지정 (없으면 자동 선택)

        Returns:
            dict: {
                'title': 메시지 제목,
                'body': 메시지 본문,
                'products': 추천 제품 목록,
                'brand': 선택된 브랜드,
                'is_valid': 검증 통과 여부
            }
        """
        print("="*60)
        print(f"메시지 생성 시작")
        print(f"- 페르소나: {persona_id}")
        print(f"- 목적: {message_purpose}")
        print(f"- 브랜드: {brand or '자동 선택'}")
        print("="*60)

        # 초기 State 생성
        initial_state = {
            "persona_id": persona_id,
            "message_purpose": message_purpose,
            "brand": brand or "",
            "persona_data": {},
            "core_needs": [],
            "lifestyle_points": [],
            "selected_brand": "",
            "brand_info": {},
            "retrieved_products": [],
            "empathy_points": [],
            "tone_examples": [],
            "title": "",
            "body": "",
            "is_valid": False,
            "validation_issues": []
        }

        # 그래프 실행
        final_state = self.graph.invoke(initial_state)

        # 결과 포맷팅
        result = {
            'title': final_state['title'],
            'body': final_state['body'],
            'products': [p['name'] for p in final_state['retrieved_products']],
            'brand': final_state['brand_info'].get('brand_name', ''),
            'is_valid': final_state['is_valid'],
            'validation_issues': final_state.get('validation_issues', [])
        }

        print("\n" + "="*60)
        print("메시지 생성 완료!")
        print("="*60)

        return result

    def generate_message_from_data(
        self,
        persona_data: dict,
        message_purpose: str = "personalized",
        brand: str = None
    ) -> dict:
        """
        마케팅 메시지 생성 (폼 데이터 직접 입력)

        Args:
            persona_data: 페르소나 정보 딕셔너리
                - age: 나이
                - gender: 성별 (F/M)
                - occupation: 직업
                - skin_type: 피부타입
                - skin_concerns: 피부 고민
                - preferred_brands: 선호 브랜드
                - lifestyle_keywords: 라이프스타일 키워드
                - product_category: 관심 제품 카테고리
            message_purpose: 메시지 목적
            brand: 특정 브랜드 지정 (없으면 자동 선택)

        Returns:
            dict: 생성된 메시지 결과
        """
        print("="*60)
        print(f"메시지 생성 시작 (폼 데이터)")
        print(f"- 나이: {persona_data.get('age')}")
        print(f"- 피부타입: {persona_data.get('skin_type')}")
        print(f"- 목적: {message_purpose}")
        print(f"- 브랜드: {brand or '자동 선택'}")
        print("="*60)

        # persona_data에 기본값 추가
        full_persona_data = {
            'persona_id': 'custom',
            'persona_name': '고객님',
            'age': persona_data.get('age', 30),
            'gender': persona_data.get('gender', 'F'),
            'occupation': persona_data.get('occupation', '직장인'),
            'skin_type': persona_data.get('skin_type', '복합성'),
            'skin_concerns': persona_data.get('skin_concerns', '수분부족'),
            'preferred_brands': persona_data.get('preferred_brands', '라네즈'),
            'shopping_pattern': '신중형',
            'price_sensitivity': 'medium',
            'lifestyle_keywords': persona_data.get('lifestyle_keywords', '직장생활, 자기계발'),
            'message_preference': '간결한 정보형',
            'purchase_history_summary': persona_data.get('product_category', '스킨케어') + ' 관심'
        }

        # 초기 State 생성 (persona_data를 직접 전달)
        initial_state = {
            "persona_id": "custom",
            "message_purpose": message_purpose,
            "brand": brand or "",
            "persona_data": full_persona_data,  # 직접 데이터 주입
            "use_csv": False,  # CSV를 사용하지 않음을 표시
            "core_needs": [],
            "lifestyle_points": [],
            "selected_brand": "",
            "brand_info": {},
            "retrieved_products": [],
            "empathy_points": [],
            "tone_examples": [],
            "title": "",
            "body": "",
            "is_valid": False,
            "validation_issues": []
        }

        # 그래프 실행
        final_state = self.graph.invoke(initial_state)

        # 결과 포맷팅
        result = {
            'title': final_state['title'],
            'body': final_state['body'],
            'products': [p['name'] for p in final_state['retrieved_products']],
            'brand': final_state['brand_info'].get('brand_name', ''),
            'is_valid': final_state['is_valid'],
            'validation_issues': final_state.get('validation_issues', [])
        }

        print("\n" + "="*60)
        print("메시지 생성 완료!")
        print("="*60)

        return result

    def print_result(self, result: dict):
        """결과 출력 헬퍼 함수"""
        print("\n" + "="*60)
        print("[MESSAGE] 생성된 마케팅 메시지")
        print("="*60)
        print(f"\n브랜드: {result['brand']}")
        print(f"\n제목 ({len(result['title'])}자):")
        print(f"  {result['title']}")
        print(f"\n본문 ({len(result['body'])}자):")
        print(f"  {result['body']}")
        print(f"\n추천 제품:")
        for i, product in enumerate(result['products'], 1):
            print(f"  {i}. {product}")
        print(f"\n검증 상태: {'[PASS] 통과' if result['is_valid'] else '[FAIL] 실패'}")
        if result['validation_issues']:
            print(f"검증 이슈: {', '.join(result['validation_issues'])}")
        print("="*60 + "\n")


# 편의 함수
def generate(persona_id: str, message_purpose: str = "personalized", brand: str = None):
    """
    빠른 메시지 생성 함수

    Example:
        >>> from src.message_generator import generate
        >>> result = generate("persona_001", "new_product")
        >>> print(result['title'])
    """
    agent = MarketingMessageAgent()
    return agent.generate_message(persona_id, message_purpose, brand)
