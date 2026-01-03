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

        # 브랜드가 지정되지 않은 경우 선호 브랜드에서 선택 (한글 이름 사용)
        if not state.get('brand'):
            preferred_brands = persona['preferred_brands'].split(',')
            selected_brand_name = preferred_brands[0].strip()
        else:
            provided = state['brand']
            # 입력값이 brand_id(영문)인 경우 한글 brand_name으로 변환
            if provided and provided in self.brands_df['brand_id'].values:
                selected_brand_name = self.brands_df[
                    self.brands_df['brand_id'] == provided
                ].iloc[0]['brand_name']
            else:
                # 이미 한글 브랜드명으로 전달된 경우 그대로 사용
                selected_brand_name = provided

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
        """노드 3: 제품 검색 (RAG) - 카테고리 우선 매칭 + 키워드 의미 기반 매칭"""
        print("\n[3. Product Retriever] 제품 검색 중...")

        persona = state['persona_data']

        # 사용자가 선택한 카테고리 (필수)
        preferred_category = persona.get('product_category', '')
        print(f"  [DEBUG] 선호 카테고리: {preferred_category}")

        if not preferred_category:
            print(f"  [WARNING] 선호 카테고리가 지정되지 않았습니다.")

        # 라이프스타일 키워드 확장 (의미 기반 매칭 - 더 넓은 범위)
        lifestyle_keywords = persona.get('lifestyle_keywords', '')
        expanded_query = self._expand_lifestyle_keywords(lifestyle_keywords)

        # 검색 쿼리 생성 (확장된 키워드 포함)
        query = f"{persona['skin_type']} 피부, {persona['skin_concerns']} 고민, {', '.join(state['core_needs'])}, {expanded_query}"

        print(f"  [DEBUG] 검색 쿼리: {query}")

        # Vector search (더 많은 결과를 가져와서 필터링)
        results = self.vector_manager.search_products(query, k=50)

        # 선택된 브랜드 + 카테고리의 제품만 엄격하게 필터링
        products = []
        fallback_products = []  # 카테고리 불일치 제품 (최후의 수단)

        for doc in results:
            # 브랜드 매칭 (필수)
            if doc.metadata.get('brand') != state['selected_brand']:
                continue

            product_category = doc.metadata.get('category', '')

            # 카테고리 매칭 (최우선)
            if preferred_category and product_category == preferred_category:
                products.append({
                    'name': doc.metadata['product_name'],
                    'category': product_category,
                    'description': doc.page_content
                })
                if len(products) >= 3:
                    break
            elif not preferred_category:
                # 카테고리 선호가 없는 경우만 다른 카테고리 허용
                fallback_products.append({
                    'name': doc.metadata['product_name'],
                    'category': product_category,
                    'description': doc.page_content
                })

        # 선호 카테고리에서 제품을 찾지 못한 경우
        if len(products) < 3:
            if len(products) == 0:
                print(f"  [ERROR] 선호 카테고리({preferred_category})에서 제품을 찾을 수 없습니다.")
                print(f"  [WARNING] 검색 쿼리를 더 넓혀서 재시도합니다.")

                # 더 넓은 쿼리로 재검색 (라이프스타일 키워드만 사용)
                broad_query = f"{expanded_query}, {persona['skin_type']}"
                broad_results = self.vector_manager.search_products(broad_query, k=100)

                for doc in broad_results:
                    if doc.metadata.get('brand') == state['selected_brand'] and \
                       doc.metadata.get('category') == preferred_category:
                        products.append({
                            'name': doc.metadata['product_name'],
                            'category': doc.metadata['category'],
                            'description': doc.page_content
                        })
                        if len(products) >= 3:
                            break
            else:
                print(f"  [INFO] 선호 카테고리({preferred_category})에서 {len(products)}개만 발견")

        # 여전히 부족하면 fallback 사용 (카테고리 선호가 없는 경우만)
        if len(products) < 3 and not preferred_category and fallback_products:
            needed = 3 - len(products)
            products.extend(fallback_products[:needed])
            print(f"  [INFO] fallback 제품 {needed}개 추가")

        # 성분 기반 추가 정보 enrichment
        enriched_products = self._enrich_with_ingredients(products, persona)

        state['retrieved_products'] = enriched_products

        print(f"  [OK] 검색된 제품: {len(enriched_products)}개")
        for p in enriched_products:
            print(f"    - {p['name']} (카테고리: {p['category']})")

        return state

    def _expand_lifestyle_keywords(self, lifestyle_keywords: str) -> str:
        """라이프스타일 키워드를 의미적으로 확장 (더 넓은 범위)"""
        # 키워드 매핑 딕셔너리 (유사 의미 단어들 - 확장판)
        keyword_mapping = {
            # 날씨 관련
            "더운 날씨": [
                "여름", "더위", "무더위", "열감", "땀", "시원한", "쿨링", "상쾌한",
                "청량", "화끈", "뜨거운", "햇빛", "자외선", "열", "더운",
                "여름철", "여름에", "덥고", "날씨가 더워", "날씨 덥"
            ],
            "추운 날씨": [
                "겨울", "추위", "건조", "갑작스런 날씨", "날씨 변화", "보습", "촉촉",
                "차가운", "찬바람", "추운", "겨울철", "겨울에", "한파", "쌀쌀",
                "날씨 추", "날씨가 추워", "추워서", "춥고", "건조한"
            ],
            "건조한 날씨": [
                "건조", "건성", "수분", "보습", "촉촉", "당김",
                "푸석", "거친", "각질", "트고", "갈라지고", "건조해서",
                "건조한", "수분 부족", "속건조", "날씨 건조", "건조함"
            ],

            # 톤 관련
            "쿨톤": [
                "차가운 톤", "블루 베이스", "핑크", "시원한 색감",
                "쿨", "청량", "푸른", "차분한", "핑크빛", "로즈", "퍼플"
            ],
            "웜톤": [
                "따뜻한 톤", "옐로우 베이스", "오렌지", "따뜻한 색감",
                "웜", "노란", "황금", "코랄", "피치", "베이지", "따스한"
            ],

            # 용도 관련
            "선물용": [
                "선물", "gift", "기프트", "특별한", "프리미엄",
                "고급", "럭셔리", "기념일", "생일", "어버이날", "발렌타인",
                "화이트데이", "크리스마스", "이벤트", "선물하기", "선물 받"
            ],
            "데일리 케어": [
                "데일리", "매일", "일상", "daily", "꾸준히", "1일1팩", "루틴",
                "평소", "자주", "계속", "꾸준", "습관", "반복", "일상적",
                "매일매일", "매일 사용", "날마다", "매번", "항상", "기본"
            ]
        }

        # 키워드 확장
        expanded = []
        for keyword in lifestyle_keywords.split(','):
            keyword = keyword.strip()
            if keyword in keyword_mapping:
                # 원본 키워드도 포함
                expanded.append(keyword)
                expanded.extend(keyword_mapping[keyword])
            else:
                expanded.append(keyword)

        return ", ".join(expanded)

    def _enrich_with_ingredients(self, products: list, persona: dict) -> list:
        """제품에 성분 정보 추가 (피부 고민 기반)"""
        # 성분 벡터 스토어가 없으면 원본 반환
        if not self.vector_manager.ingredients_store:
            return products

        # 피부 고민으로 관련 성분 검색
        skin_concerns = persona.get('skin_concerns', '')
        if not skin_concerns:
            return products

        print(f"  [Ingredients] 피부 고민 '{skin_concerns}'에 맞는 성분 검색 중...")

        # 성분 검색
        ingredient_results = self.vector_manager.search_ingredients(
            query=f"{skin_concerns} 피부 고민에 좋은 성분",
            k=5
        )

        if not ingredient_results:
            return products

        # 검색된 성분 정보 정리
        ingredients_info = []
        for ing_doc in ingredient_results:
            ing_name_kor = ing_doc.metadata.get('ingredient_kor', '')
            ing_name_eng = ing_doc.metadata.get('ingredient_eng', '')
            ing_function = ing_doc.metadata.get('function', '')
            ing_description = ing_doc.metadata.get('description', '')

            # function이 비어있으면 description의 첫 100자 사용
            if not ing_function or ing_function == 'nan':
                ing_function = ing_description[:100] if ing_description else ''

            if ing_name_kor and ing_name_kor not in ['제목 없음', 'No Title']:
                ingredients_info.append({
                    'name': ing_name_kor,
                    'name_eng': ing_name_eng,
                    'function': ing_function
                })

        if ingredients_info:
            print(f"  [Ingredients] 발견된 성분: {', '.join([i['name'] for i in ingredients_info[:3]])}")

        # 각 제품 설명에 성분 정보 추가
        for product in products:
            if ingredients_info:
                ingredient_text = " | ".join([
                    f"{ing['name']}({ing['function'][:30]}...)" if len(ing['function']) > 30
                    else f"{ing['name']}({ing['function']})"
                    for ing in ingredients_info[:3]
                ])
                product['description'] += f"\n\n[추천 성분] {ingredient_text}"
                product['ingredients'] = ingredients_info[:3]

        return products

    def review_context_enricher(self, state: MessageGenerationState) -> MessageGenerationState:
        """노드 4: 리뷰 컨텍스트 추가 - 라이프스타일 키워드 기반"""
        print("\n[4. Review Context Enricher] 리뷰 분석 중...")

        persona = state['persona_data']

        # 라이프스타일 키워드 확장
        lifestyle_keywords = persona.get('lifestyle_keywords', '')
        expanded_query = self._expand_lifestyle_keywords(lifestyle_keywords)

        # 유사 리뷰 검색 (확장된 키워드로)
        query = f"{persona['age']}세 {persona['skin_type']} {expanded_query}"
        print(f"  [DEBUG] 리뷰 검색 쿼리: {query}")
        review_results = self.vector_manager.search_reviews(query, k=3)

        reviews_text = "\n".join([doc.page_content for doc in review_results])

        # 공감 포인트 추출
        prompt = REVIEW_ENRICHER_PROMPT.format(
            reviews=reviews_text,
            age=persona['age'],
            occupation=persona.get('occupation', ''),
            lifestyle_keywords=lifestyle_keywords
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
            persona_name=persona.get('persona_name', '고객님'),
            age=persona['age'],
            gender='여성' if persona.get('gender', 'F') == 'F' else '남성',
            occupation=persona.get('occupation', ''),
            skin_concerns=persona['skin_concerns'],
            lifestyle_keywords=persona.get('lifestyle_keywords', ''),
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
