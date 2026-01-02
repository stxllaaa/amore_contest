"""
LangGraph 노드 구현
각 노드는 State를 받아 처리 후 업데이트된 State를 반환
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import TypedDict, List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from .prompts import *


# State 정의
class MessageGenerationState(TypedDict):
    # 입력
    persona_id: str
    message_purpose: str
    brand: str  # optional

    # 중간 결과
    persona_data: Dict
    core_needs: List[str]
    lifestyle_points: List[str]
    selected_brand: str
    brand_info: Dict
    retrieved_products: List[Dict]
    empathy_points: List[str]
    tone_examples: List[str]

    # 최종 결과
    title: str
    body: str
    is_valid: bool
    validation_issues: List[str]


class GraphNodes:
    """LangGraph 노드 클래스"""

    def __init__(self, db_path: str, vector_manager):
        self.db_path = Path(db_path)
        self.vector_manager = vector_manager

        # LLM 초기화
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("MODEL_NAME", "models/gemini-2.5-flash"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # 데이터 로드
        self.personas_df = pd.read_csv(
            Path(os.getenv("CUSTOMERS_DB_PATH", "./customers_db")) / "customer_personas.csv",
            encoding='utf-8-sig'
        )
        self.brands_df = pd.read_csv(
            self.db_path / "brand_info.csv",
            encoding='utf-8-sig'
        )

    def persona_analyzer(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 1: 페르소나 분석"""
        print("\n[1. Persona Analyzer] 페르소나 분석 중...")

        # use_csv 플래그 확인 (폼 데이터 직접 사용 시 CSV 로드 스킵)
        if state.get('use_csv', True) and state.get('persona_data'):
            # 이미 persona_data가 있으면 그대로 사용
            persona = state['persona_data']
        elif state.get('use_csv', True):
            # CSV에서 페르소나 데이터 로드
            persona = self.personas_df[
                self.personas_df['persona_id'] == state['persona_id']
            ].iloc[0].to_dict()
        else:
            # 폼 데이터로 전달된 persona_data 사용
            persona = state['persona_data']

        # 프롬프트 생성
        prompt = PERSONA_ANALYZER_PROMPT.format(**persona)

        # LLM 호출
        messages = [
            SystemMessage(content="당신은 고객 분석 전문가입니다."),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)

        # JSON 파싱 (개선된 버전)
        try:
            response_text = response.content.strip()

            # Markdown 코드 블록 제거
            if response_text.startswith("```"):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])

            result = json.loads(response_text)

        except json.JSONDecodeError as e:
            print(f"  [WARNING] JSON 파싱 실패: {e}")
            print(f"  [DEBUG] LLM 응답 (처음 200자): {response.content[:200]}")
            result = {
                "core_needs": [persona['skin_concerns']],
                "lifestyle_points": [persona['lifestyle_keywords']],
                "recommended_categories": ["스킨케어"]
            }
            print(f"  [FALLBACK] 기본값 사용")

        # State 업데이트
        state['persona_data'] = persona
        state['core_needs'] = result.get('core_needs', [persona['skin_concerns']])
        state['lifestyle_points'] = result.get('lifestyle_points', [persona['lifestyle_keywords']])

        print(f"  [OK] 핵심 니즈: {state['core_needs']}")
        return state

    def brand_selector(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 2: 브랜드 선택"""
        print("\n[2. Brand Selector] 브랜드 선택 중...")

        persona = state['persona_data']

        # 브랜드가 지정되지 않은 경우 선호 브랜드에서 선택
        if not state.get('brand'):
            preferred_brands = persona['preferred_brands'].split(',')
            selected_brand_name = preferred_brands[0].strip()
        else:
            selected_brand_name = state['brand']

        # 브랜드 정보 로드 (brand_name으로 검색)
        brand_df_filtered = self.brands_df[
            self.brands_df['brand_name'] == selected_brand_name
        ]

        if len(brand_df_filtered) == 0:
            raise ValueError(f"브랜드를 찾을 수 없습니다: {selected_brand_name}")

        brand_info = brand_df_filtered.iloc[0].to_dict()
        selected_brand = brand_info['brand_id']

        state['selected_brand'] = selected_brand
        state['brand_info'] = brand_info

        print(f"  [OK] 선택된 브랜드: {brand_info['brand_name']}")
        return state

    def product_retriever(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 3: 제품 검색 (RAG)"""
        print("\n[3. Product Retriever] 제품 검색 중...")

        persona = state['persona_data']

        # 검색 쿼리 생성
        query = f"{persona['skin_type']} 피부, {persona['skin_concerns']} 고민, {', '.join(state['core_needs'])}"

        # Vector search (더 많은 결과를 가져와서 브랜드 필터링)
        results = self.vector_manager.search_products(query, k=20)

        # 선택된 브랜드의 제품만 필터링
        products = []
        for doc in results:
            if doc.metadata.get('brand') == state['selected_brand']:
                products.append({
                    'name': doc.metadata['product_name'],
                    'category': doc.metadata['category'],
                    'description': doc.page_content
                })
                if len(products) >= 3:
                    break

        state['retrieved_products'] = products

        print(f"  [OK] 검색된 제품: {len(products)}개")
        return state

    def review_context_enricher(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 4: 리뷰 컨텍스트 추가"""
        print("\n[4. Review Context Enricher] 리뷰 분석 중...")

        persona = state['persona_data']

        # 유사 리뷰 검색
        query = f"{persona['age']}세 {persona['occupation']} {persona['lifestyle_keywords']}"
        review_results = self.vector_manager.search_reviews(query, k=3)

        reviews_text = "\n".join([doc.page_content for doc in review_results])

        # 공감 포인트 추출
        prompt = REVIEW_ENRICHER_PROMPT.format(
            reviews=reviews_text,
            age=persona['age'],
            occupation=persona['occupation'],
            lifestyle_keywords=persona['lifestyle_keywords']
        )

        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)

        # JSON 파싱 (개선된 버전)
        try:
            response_text = response.content.strip()

            # Markdown 코드 블록 제거
            if response_text.startswith("```"):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])

            result = json.loads(response_text)
            empathy_points = result.get('empathy_points', state['lifestyle_points'])

        except json.JSONDecodeError as e:
            print(f"  [WARNING] JSON 파싱 실패: {e}")
            print(f"  [FALLBACK] 라이프스타일 키워드 사용")
            empathy_points = state['lifestyle_points']

        state['empathy_points'] = empathy_points

        print(f"  [OK] 공감 포인트: {empathy_points}")
        return state

    def tone_adapter(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 5: 톤 어댑터"""
        print("\n[5. Tone Adapter] 톤 예시 검색 중...")

        # 브랜드별 톤 예시 검색
        tone_results = self.vector_manager.search_tone_examples(
            state['selected_brand'],
            k=3
        )

        tone_examples = [doc.page_content for doc in tone_results]
        state['tone_examples'] = tone_examples

        print(f"  [OK] 톤 예시: {len(tone_examples)}개")
        return state

    def message_generator(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 6: 메시지 생성"""
        print("\n[6. Message Generator] 메시지 생성 중...")

        persona = state['persona_data']
        brand_info = state['brand_info']

        # 제품 정보 포맷팅
        products_text = "\n".join([
            f"- {p['name']} ({p['category']}): {p['description'][:100]}..."
            for p in state['retrieved_products']
        ])

        # 톤 예시 포맷팅
        tone_text = "\n".join([f"예시{i+1}: {ex}" for i, ex in enumerate(state['tone_examples'])])

        # 프롬프트 생성
        prompt = MESSAGE_GENERATOR_PROMPT.format(
            brand_name=brand_info['brand_name'],
            target_age=brand_info['target_age'],
            brand_concept=brand_info['brand_concept'],
            persona_name=persona['persona_name'],
            age=persona['age'],
            gender='여성' if persona['gender'] == 'F' else '남성',
            occupation=persona['occupation'],
            skin_concerns=persona['skin_concerns'],
            lifestyle_keywords=persona['lifestyle_keywords'],
            products=products_text,
            tone_examples=tone_text,
            empathy_points=", ".join(state['empathy_points']),
            message_purpose_desc=MESSAGE_PURPOSE_DESCRIPTIONS.get(
                state['message_purpose'], "개인화 메시지"
            ),
            tone_style=TONE_STYLE_DESCRIPTIONS.get(
                state['selected_brand'], "친근한 톤"
            )
        )

        # LLM 호출
        messages = [
            SystemMessage(content="당신은 아모레퍼시픽의 CRM 마케팅 전문가입니다."),
            HumanMessage(content=prompt)
        ]
        response = self.llm.invoke(messages)

        # JSON 파싱 (개선된 버전)
        try:
            # 응답 내용 로깅
            response_text = response.content.strip()

            # Markdown 코드 블록 제거 (```json ... ``` 형식)
            if response_text.startswith("```"):
                # ```json 또는 ``` 제거
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])  # 첫 줄과 마지막 줄 제거

            # JSON 파싱
            result = json.loads(response_text)
            state['title'] = result.get('title', f"{brand_info['brand_name']} 신제품 추천")
            state['body'] = result.get('body', "고객님께 어울리는 제품을 준비했습니다.")

            print(f"  [OK] 제목: {state['title'][:30]}...")

        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 상세 로깅
            print(f"  [WARNING] JSON 파싱 실패: {e}")
            print(f"  [DEBUG] LLM 응답 (처음 200자): {response.content[:200]}")

            # 기본값 사용
            state['title'] = f"{brand_info['brand_name']} 신제품 추천"
            state['body'] = "고객님께 어울리는 제품을 준비했습니다."
            print(f"  [FALLBACK] 기본 메시지 사용")

        except Exception as e:
            # 기타 에러
            print(f"  [ERROR] 예상치 못한 에러: {e}")
            state['title'] = f"{brand_info['brand_name']} 신제품 추천"
            state['body'] = "고객님께 어울리는 제품을 준비했습니다."

        return state

    def quality_validator(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 7: 품질 검증"""
        print("\n[7. Quality Validator] 품질 검증 중...")

        title = state['title']
        body = state['body']

        title_len = len(title)
        body_len = len(body)

        # 기본 검증
        issues = []
        if title_len > 40:
            issues.append(f"제목이 너무 깁니다 ({title_len}자)")
        if body_len > 350:
            issues.append(f"본문이 너무 깁니다 ({body_len}자)")

        # 금칙어 체크 (간단 버전)
        forbidden_words = ['LG생활건강', '코스맥스', '에스티로더']
        for word in forbidden_words:
            if word in title or word in body:
                issues.append(f"금칙어 포함: {word}")

        is_valid = len(issues) == 0

        state['is_valid'] = is_valid
        state['validation_issues'] = issues

        if is_valid:
            print("  [OK] 검증 통과!")
        else:
            print(f"  [FAIL] 검증 실패: {issues}")

        return state
