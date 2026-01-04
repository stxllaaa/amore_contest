# 아모레퍼시픽 CRM 마케팅 메시지 생성 시스템

아모레퍼시픽 브랜드 데이터를 이용해 고객 페르소나 기반의 개인화 마케팅 메시지(제목 + 본문)를 자동으로 생성하는 시스템입니다. LangGraph 기반 워크플로우와 RAG(벡터 검색)를 활용해 제품 추천, 리뷰 컨텍스트 반영, 브랜드 톤 적용, 품질 검증을 수행합니다.

## 주요 기능

- **페르소나 기반 개인화**: 고객의 나이, 피부타입, 라이프스타일을 분석하여 맞춤 메시지 생성
- **브랜드별 톤앤매너**: 에뛰드, 라네즈, 헤라, 설화수, 아이오페 각 브랜드의 고유한 톤 반영
- **RAG 기반 제품 추천**: 벡터 검색을 통해 고객에게 최적화된 제품 자동 선택
- **리뷰 컨텍스트 활용**: 유사 고객의 리뷰를 분석하여 공감 포인트 도출
- **7단계 워크플로우**: LangGraph로 구성된 체계적인 메시지 생성 파이프라인
- **품질 자동 검증**: 제목/본문 길이, 금칙어, 톤 일관성 자동 체크

## 🔧 핵심 변경 사항

- 데이터는 브랜드별 개별 CSV 대신 통합된 파일을 사용합니다 (자세한 내용은 `DATA_STRUCTURE.md` 참고).
  - 제품: `brands_db/products_db/all_products.csv`
  - 리뷰: `brands_db/reviews_db/all_reviews.csv` (※ `lifestyle` 컬럼이 있어야 벡터 스토어에 포함됩니다)
  - 브랜드 톤: `brands_db/brand_tone_corpus/marketing_tone_info.xlsx` (실제 마케팅 문장 사용)
- 벡터 스토어는 `src.embeddings.VectorStoreManager`가 생성/로딩합니다. (FAISS 사용)

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────┐   │
│  │   Persona    │──>│    Brand     │──>│   Product     │   │
│  │   Analyzer   │   │   Selector   │   │  Retriever    │   │
│  └──────────────┘   └──────────────┘   └───────────────┘   │
│         │                                      │            │
│         v                                      v            │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────┐   │
│  │    Review    │──>│     Tone     │──>│   Message     │   │
│  │   Enricher   │   │   Adapter    │   │  Generator    │   │
│  └──────────────┘   └──────────────┘   └───────────────┘   │
│                                              │              │
│                                              v              │
│                                      ┌───────────────┐      │
│                                      │   Quality     │      │
│                                      │  Validator    │      │
│                                      └───────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
                ┌───────────────────────────┐
                │    FAISS Vector Stores     │
                ├───────────────────────────┤
                │  • Products (92개 제품)    │
                │  • Tone Corpus (99개 예시) │
                │  • Reviews (~6,141개 리뷰, 5개 브랜드 통합)    │
                └───────────────────────────┘
```

## 🚀 빠른 시작

1) 의존성 설치

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) 환경 변수 설정

```bash
cp .env.example .env
# .env에 OPENAI_API_KEY, GOOGLE_API_KEY 등을 설정하세요
```

3) 로컬 서버 실행 (개발용)

```bash
python app.py
# → http://localhost:5000
```

4) 파이썬 API 사용 예시

```python
from src.message_generator import MarketingMessageAgent
agent = MarketingMessageAgent(db_path="./brands_db")
result = agent.generate_message("persona_001", "personalized")
print(result)
```

## 프로젝트 구조

---

## 📁 데이터 구조 요약

- `brands_db/`
  - `brand_info.csv` — 브랜드 메타 정보
  - `products_db/all_products.csv` — 모든 제품 통합 CSV
  - `reviews_db/all_reviews.csv` — 통합 리뷰 CSV (벡터화 시 `lifestyle` 필터 적용)
  - `brand_tone_corpus/marketing_tone_info.xlsx` — 브랜드별 마케팅 문장 (운영 기준: `marketing_tone_info.csv` 사용; XLSX는 보관용이며 리포지토리에 CSV(`marketing_tone_info.csv`)가 포함되어 있어 런타임에 OpenPyXL/XLSX 지원이 없어도 동작합니다)
  - (참고) per-brand tone CSV는 보관용/레거시이며 시스템은 통합 CSV(`marketing_tone_info.csv`)를 사용합니다
- `ingredients_db/cosmetic_ingredients.csv` — 성분 데이터 (선택적)
- `vector_store/` — FAISS 스토어(자동 생성)

자세한 컬럼 및 마이그레이션 가이드는 `DATA_STRUCTURE.md`를 참고하세요.

```
amore/
├── brands_db/                    # 브랜드 데이터베이스
│   ├── brand_info.csv           # 5개 브랜드 정보
│   ├── products_db/             # 통합 제품 데이터
│   │   └── all_products.csv
│   ├── brand_tone_corpus/       # 브랜드 톤 코퍼스 (마케팅 문장 통합 CSV)
│   │   ├── marketing_tone_info.xlsx
│   │   └── marketing_tone_info.csv   # 시스템에서 사용하는 통합 CSV (xlsx → csv 자동 변환)
│   └── reviews_db/              # 통합 리뷰 데이터 (5개 브랜드 통합, 약 6,141개 리뷰)
│       └── all_reviews.csv
├── customers_db/                # 고객 페르소나 데이터
│   ├── customer_personas.csv   # 8개 페르소나 (CSV)
│   └── customer_personas.json  # 8개 페르소나 (JSON)
├── src/                         # 소스 코드
│   ├── __init__.py
│   ├── embeddings.py           # 벡터 스토어 관리
│   ├── prompts.py              # 프롬프트 템플릿
│   ├── graph_nodes.py          # LangGraph 노드 구현
│   ├── graph_builder.py        # LangGraph 워크플로우
│   └── message_generator.py    # 메인 에이전트
├── tests/                       # 테스트 코드
│   ├── __init__.py
│   └── test_generator.py
├── vector_store/                # FAISS 벡터 스토어 (자동 생성)
├── requirements.txt
├── .env.example
└── README.md
```

## 사용 방법

### 1. 기본 사용법

```python
from src.message_generator import MarketingMessageAgent

# 에이전트 초기화 (최초 실행 시 벡터 스토어 자동 생성)
agent = MarketingMessageAgent(db_path="./brands_db")

# 메시지 생성
result = agent.generate_message(
    persona_id="persona_001",       # 고객 페르소나 ID
    message_purpose="personalized",  # 메시지 목적
    brand=None                       # 브랜드 (None이면 자동 선택)
)

# 결과 출력
agent.print_result(result)
```

### 2. 메시지 목적 옵션

- `new_product`: 신상품 소개
- `repurchase`: 재구매 유도
- `promotion`: 프로모션/할인 안내
- `seasonal`: 계절별 추천
- `personalized`: 개인 맞춤 추천 (기본값)

### 3. 다양한 사용 예시

#### 예시 1: 신상품 소개 메시지

```python
result = agent.generate_message(
    persona_id="persona_001",  # 19세 여성, 대학생, 에뛰드 선호
    message_purpose="new_product"
)

# 결과:
# {
#   'title': '지금 가장 핫한 신상! 너만의 컬러 찾아봐',
#   'body': '요즘 대학가에서 난리난 신상품 알아? 피부 걱정은 이제 그만...',
#   'products': ['에뛰드 순정 토너', '에뛰드 AC클린업 젤로션', ...],
#   'brand': '에뛰드',
#   'is_valid': True
# }
```

#### 예시 2: 특정 브랜드 지정

```python
result = agent.generate_message(
    persona_id="persona_006",  # 48세 여성, 전문직, 고급 선호
    message_purpose="seasonal",
    brand="sulwhasoo"  # 설화수 지정
)

# 결과: 설화수의 고급스러운 톤으로 작성된 메시지
```

#### 예시 3: 남성 고객 메시지

```python
result = agent.generate_message(
    persona_id="persona_004",  # 35세 남성, 직장인
    message_purpose="repurchase"
)

# 결과: 아이오페 브랜드로 남성 고객 맞춤 메시지
```

### Web API

서버를 실행하면 다음 엔드포인트를 사용할 수 있습니다 (Flask 기반):

- `POST /api/generate` — 메시지 생성
  - 요청 예시 (JSON):
    ```json
    {
      "age": 30,
      "gender": "여성",
      "skin_type": "복합성",
      "product_category": "skin",
      "message_purpose": "personalized",
      "brand": "laneige"
    }
    ```
  - 응답: `{ "success": true, "result": { /* 생성 결과 */ } }`

- `GET /api/brands` — 브랜드 목록 반환

- `POST /api/save` — 생성된 마케팅 자산을 CSV로 저장

### 4. 편의 함수 사용

```python
from src.message_generator import generate

# 간단한 호출
result = generate("persona_001", "new_product")
print(result['title'])
print(result['body'])
```

## 테스트 실행

```bash
# 전체 테스트 실행
python tests/test_generator.py

# 출력 예시:
# ============================================================
# 아모레퍼시픽 CRM 마케팅 메시지 생성 시스템 테스트
# ============================================================
#
# [테스트 1] 기본 메시지 생성 (persona_001)
# [OK] 기본 메시지 생성 테스트 통과
#
# [테스트 2] 신상품 소개 메시지 (persona_002)
# [OK] 신상품 소개 메시지 테스트 통과
#
# ... (이하 테스트 결과)
#
# ============================================================
# 모든 테스트 통과!
# ============================================================
```

## 데이터베이스 구성

### 브랜드 정보 (5개 브랜드)

| 브랜드 | 타겟 연령 | 컨셉 |
|--------|-----------|------|
| 에뛰드 | 10-25세 | 발랄하고 트렌디한 젊은 감성 |
| 라네즈 | 23-29세 | 친근하고 실용적인 일상 뷰티 |
| 헤라 | 30-49세 | 세련되고 프로페셔널한 프리미엄 |
| 설화수 | 45-60세 | 한방 럭셔리, 전통과 과학의 조화 |
| 아이오페 | 30-49세 | 과학적 스킨케어, 남성 타겟 포함 |

### 고객 페르소나 (8명)

- **persona_001**: 19세 여성, 대학생, 에뛰드 선호
- **persona_002**: 26세 여성, 마케터, 라네즈 선호
- **persona_003**: 32세 여성, IT개발자, 헤라 선호
- **persona_004**: 35세 남성, 직장인, 아이오페 선호
- **persona_005**: 42세 여성, 디자이너, 헤라 선호
- **persona_006**: 48세 여성, 전문직, 설화수 선호
- **persona_007**: 28세 여성, 교사, 라네즈 선호
- **persona_008**: 23세 여성, 신입사원, 에뛰드 선호

## 워크플로우 상세 설명

### 1. Persona Analyzer (페르소나 분석)
- 입력: 고객 페르소나 ID
- 처리: 고객의 피부타입, 나이, 직업, 라이프스타일 분석
- 출력: 핵심 니즈, 라이프스타일 키워드, 추천 카테고리

### 2. Brand Selector (브랜드 선택)
- 입력: 고객 선호 브랜드 또는 명시적 브랜드 지정
- 처리: 고객에게 최적화된 브랜드 선택
- 출력: 선택된 브랜드 정보 (컨셉, 타겟 연령 등)

### 3. Product Retriever (제품 검색 - RAG)
- 입력: 고객 니즈, 선택된 브랜드
- 처리: FAISS 벡터 검색으로 유사 제품 탐색
- 출력: 상위 3개 추천 제품

### 4. Review Context Enricher (리뷰 컨텍스트 추가)
- 입력: 고객 프로필, 선택된 제품
- 처리: 유사 고객의 라이프스타일 리치 리뷰 분석
- 출력: 공감 포인트 추출

### 5. Tone Adapter (톤 어댑터)
- 입력: 선택된 브랜드
- 처리: 브랜드별 톤 코퍼스에서 예시 검색
- 출력: 브랜드 톤앤매너 예시

### 6. Message Generator (메시지 생성)
- 입력: 모든 수집된 컨텍스트
- 처리: GPT-4o-mini로 제목+본문 생성
- 출력: 제목 (40자 이내), 본문 (350자 이내)

### 7. Quality Validator (품질 검증)
- 입력: 생성된 메시지
- 처리: 길이 제한, 금칙어, 톤 일관성 체크
- 출력: 검증 통과 여부, 이슈 목록

## 기술 스택

- **LangChain**: LLM 통합 및 체인 구성
- **LangGraph**: 상태 기반 워크플로우 관리
- **OpenAI GPT-4o-mini**: 메시지 생성 LLM
- **OpenAI Embeddings**: text-embedding-3-small
- **FAISS**: 벡터 유사도 검색
- **Pandas**: 데이터 처리
- **Python-dotenv**: 환경 변수 관리

## 환경 변수 설정

`.env` 파일에서 다음 항목을 설정할 수 있습니다:

```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-your-api-key-here

# 모델 설정
MODEL_NAME=gpt-4o-mini                      # LLM 모델
EMBEDDING_MODEL=text-embedding-3-small       # 임베딩 모델
TEMPERATURE=0.7                              # 생성 온도 (0.0-1.0)

# 경로 설정
BRANDS_DB_PATH=./brands_db
CUSTOMERS_DB_PATH=./customers_db
VECTOR_STORE_PATH=./vector_store

# 메시지 제약 조건
MAX_TITLE_LENGTH=40      # 제목 최대 길이 (글자 수)
MAX_BODY_LENGTH=350      # 본문 최대 길이 (글자 수)
```

## 시스템 평가 및 테스트

### 평가 시스템 개요

전체 조합 테스트 및 LLM 기반 자동 평가 시스템이 포함되어 있습니다.

**주요 기능:**
- 모든 페르소나 × 모든 메시지 목적 = 40개 조합 자동 테스트
- LLM 기반 4가지 품질 평가 (브랜드 톤, 페르소나 적합, 자연스러움, 구매 유도력)
- 제약 조건 자동 검증
- 브랜드 톤 특징 분석
- 8가지 시각화 차트 자동 생성

### 빠른 시작

```bash
# 1. 평가 모듈 패키지 설치
pip install -r evaluation/requirements.txt

# 2. 전체 평가 실행 (테스트 + 시각화)
python run_evaluation.py

# 또는 개별 실행
python evaluation/test_all_combinations.py  # 테스트만
python evaluation/visualize_results.py      # 시각화만
```

**예상 소요 시간:** 약 20-30분 (40개 메시지 생성 및 평가)

### 평가 결과

**출력 파일:**
- `evaluation/results/test_results_YYYYMMDD_HHMMSS.csv` - 전체 평가 결과
- `evaluation/plots/01_brand_scores.png` - 브랜드별 점수
- `evaluation/plots/02_purpose_scores.png` - 메시지 목적별 점수
- `evaluation/plots/03_radar_chart.png` - 레이더 차트
- `evaluation/plots/04_constraints_pie.png` - 제약 조건 통과율
- `evaluation/plots/05_tone_consistency_heatmap.png` - 톤 일관성 히트맵
- `evaluation/plots/06_generation_time.png` - 생성 시간 분포
- `evaluation/plots/07_score_boxplot.png` - 점수 분포
- `evaluation/plots/08_comprehensive_dashboard.png` - 종합 대시보드

자세한 내용은 [evaluation/README.md](evaluation/README.md)를 참조하세요.

## 💡 운영/유의사항

- 리뷰는 `lifestyle` 정보가 있는 경우에만 임베딩에 포함됩니다.
- 브랜드 톤 데이터는 실제 마케팅 문장을 사용하므로 가공에 유의하세요.
- 벡터 스토어를 재생성하려면 `rm -rf ./vector_store` 후 `VectorStoreManager.build_all_stores()`를 실행하세요.

## 트러블슈팅

### 1. 벡터 스토어가 생성되지 않는 경우

```python
# 벡터 스토어 강제 재생성
agent = MarketingMessageAgent(db_path="./brands_db")
agent.vector_manager.build_all_stores()
```

### 2. OpenAI API 오류

- `.env` 파일에 올바른 API 키가 설정되어 있는지 확인
- API 사용량 한도를 초과하지 않았는지 확인

### 3. 인코딩 오류 (Windows)

- CSV 파일은 모두 UTF-8-sig로 인코딩됨
- 콘솔 출력이 깨지는 경우, 이는 Windows 콘솔의 cp949 인코딩 제한이며 데이터 자체는 정상

## 라이센스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.
