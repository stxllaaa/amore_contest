"""
프롬프트 템플릿 모음
각 LangGraph 노드에서 사용하는 프롬프트
"""

# 1. Persona Analyzer 프롬프트
PERSONA_ANALYZER_PROMPT = """당신은 고객 페르소나 분석 전문가입니다.

주어진 고객 정보를 분석하여 핵심 니즈와 마케팅 키워드를 추출하세요.

## 고객 정보
- 이름: {persona_name}
- 나이: {age}세, 성별: {gender}
- 직업: {occupation}
- 피부타입: {skin_type}
- 피부고민: {skin_concerns}
- 쇼핑패턴: {shopping_pattern}
- 가격민감도: {price_sensitivity}
- 라이프스타일: {lifestyle_keywords}
- 선호 브랜드: {preferred_brands}

## 분석 과제
1. 이 고객의 핵심 니즈 3가지
2. 공감할 수 있는 라이프스타일 키워드
3. 추천 제품 카테고리

JSON 형식으로 응답하세요:
{{
  "core_needs": ["니즈1", "니즈2", "니즈3"],
  "lifestyle_points": ["포인트1", "포인트2"],
  "recommended_categories": ["카테고리1", "카테고리2"]
}}
"""

# 2. Product Retriever 프롬프트
PRODUCT_SEARCH_QUERY_PROMPT = """고객 프로필을 기반으로 제품 검색 쿼리를 생성하세요.

## 고객 정보
- 피부타입: {skin_type}
- 피부고민: {skin_concerns}
- 핵심 니즈: {core_needs}
- 선호 브랜드: {preferred_brands}

자연어 검색 쿼리를 생성하세요 (100자 이내):
"""

# 3. Review Context Enricher 프롬프트
REVIEW_ENRICHER_PROMPT = """선택된 제품의 리뷰를 분석하여 공감 포인트를 추출하세요.

## 유사 고객 리뷰
{reviews}

## 고객 프로필
- 나이: {age}세
- 직업: {occupation}
- 라이프스타일: {lifestyle_keywords}

이 리뷰들에서 고객이 공감할 만한 포인트 2-3개를 추출하세요.
JSON 형식으로 응답:
{{
  "empathy_points": ["포인트1", "포인트2"]
}}
"""

# 4. Message Generator 프롬프트
MESSAGE_GENERATOR_PROMPT = """아모레퍼시픽 CRM 마케팅 메시지를 생성하세요.

## 브랜드 정보
브랜드: {brand_name}
타겟 연령: {target_age}
브랜드 컨셉: {brand_concept}

## 고객 정보
- 이름: {persona_name} ({age}세, {gender})
- 직업: {occupation}
- 피부 고민: {skin_concerns}
- 라이프스타일: {lifestyle_keywords}
- 가격 민감도: {price_sensitivity}

## 추천 제품
{products}

## 브랜드 톤 참고 예시
{tone_examples}

## 고객 공감 포인트
{empathy_points}

## 메시지 목적
{message_purpose_desc}

## 작성 요구사항
1. 제목: 40자 이내, 고객의 관심을 끄는 문구
2. 본문: 350자 이내, 자연스럽고 감성적인 문장
3. 브랜드 톤앤매너 반영 ({tone_style})
4. 고객의 라이프스타일과 니즈에 공감
5. 제품의 핵심 혜택 강조
6. 가격 민감도 반영:
   - Low (가성비 중시): "합리적인 가격", "가성비 좋은", "똑똑한 선택" 등의 표현 사용
   - High (고가 선호): "프리미엄", "럭셔리한 경험", "특별한" 등의 표현 사용
   - Mid (중간): 가격에 대한 언급 최소화, 제품 가치와 효능에 집중

JSON 형식으로 응답:
{{
  "title": "메시지 제목",
  "body": "메시지 본문"
}}
"""

# 5. Quality Validator 프롬프트
QUALITY_VALIDATOR_PROMPT = """생성된 마케팅 메시지의 품질을 검증하세요.

## 생성된 메시지
제목: {title}
본문: {body}

## 브랜드 정보
브랜드: {brand}
브랜드 톤: {tone_features}

## 검증 항목
1. 제목 길이 (40자 이내): {title_length}자
2. 본문 길이 (350자 이내): {body_length}자
3. 브랜드 톤 일관성
4. 금칙어 포함 여부 (경쟁사 브랜드명 등)
5. 자연스러운 문장

검증 결과를 JSON으로 응답:
{{
  "is_valid": true/false,
  "issues": ["이슈1", "이슈2"],  // 없으면 빈 리스트
  "suggestions": ["수정 제안1"]  // 없으면 빈 리스트
}}
"""

# 메시지 목적별 설명
MESSAGE_PURPOSE_DESCRIPTIONS = {
    "new_product": "신상품 출시를 소개하고 고객의 호기심을 자극하는 메시지",
    "repurchase": "기존에 사용했던 제품의 재구매를 유도하는 메시지",
    "promotion": "특별 할인이나 프로모션을 알리는 메시지",
    "seasonal": "계절 변화에 맞는 제품을 추천하는 메시지",
    "personalized": "고객 맞춤 제품을 추천하는 개인화 메시지"
}

# 톤 스타일 설명
TONE_STYLE_DESCRIPTIONS = {
    "etude": "발랄하고 트렌디한 톤, 이모티콘 사용, 반말",
    "laneige": "친근하고 실용적인 톤, ~해요 말투, 공감형",
    "hera": "세련되고 프로페셔널한 톤, 격식체, 우아함",
    "sulwhasoo": "고급스럽고 전통적인 톤, 한자어 사용, 격식 높음",
    "iope": "과학적이고 전문적인 톤, 근거 기반, 신뢰감"
}
