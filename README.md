# 아모레퍼시픽 CRM 마케팅 메시지 자동 생성 시스템

LangGraph와 RAG 기술을 활용한 개인화 마케팅 메시지 자동 생성 시스템입니다.

## 주요 기능

- **페르소나 기반 개인화**: 고객의 나이, 피부타입, 라이프스타일을 분석하여 맞춤 메시지 생성
- **브랜드별 톤앤매너**: 에뛰드, 라네즈, 헤라, 설화수, 아이오페 각 브랜드의 고유한 톤 반영
- **RAG 기반 제품 추천**: 벡터 검색을 통해 고객에게 최적화된 제품 자동 선택
- **리뷰 컨텍스트 활용**: 유사 고객의 리뷰를 분석하여 공감 포인트 도출
- **7단계 워크플로우**: LangGraph로 구성된 체계적인 메시지 생성 파이프라인
- **품질 자동 검증**: 제목/본문 길이, 금칙어, 톤 일관성 자동 체크

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
                │  • products (brands_db/products_db/all_products.csv)
                │  • tone (brands_db/brand_tone_corpus/marketing_tone_info.xlsx)
                │  • reviews (brands_db/reviews_db/all_reviews.csv)
                └───────────────────────────┘
```

## 설치 방법

### 1. 필수 요구사항

- Python 3.9 이상
- Google Gemini API 키 (`GOOGLE_API_KEY`), 또는 Gemini 접근 권한

### 2. 저장소 클론 및 패키지 설치

```bash
# 저장소 클론 (또는 프로젝트 디렉토리로 이동)
cd amore_contest

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 Google API 키 입력
# GOOGLE_API_KEY=your-google-api-key-here
```

## 프로젝트 구조

```
amore/
├── brands_db/                    # 브랜드 데이터베이스
│   ├── brand_info.csv            # 브랜드 메타 정보
│   ├── products_db/              # 제품 데이터(통합 CSV)
│   │   └── all_products.csv      # 모든 브랜드/제품을 통합한 파일
│   ├── brand_tone_corpus/        # 브랜드 톤 코퍼스
│   │   └── marketing_tone_info.xlsx  # 마케팅 문구 예시 통합 파일
│   └── reviews_db/               # 리뷰 데이터(통합 CSV)
│       └── all_reviews.csv       # 모든 리뷰를 통합한 파일 (lifestyle 포함된 리뷰만 사용)
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
├── tests/                        # 테스트 코드
│   ├── __init__.py
│   └── test_generator.py
├── vector_store/                 # FAISS 벡터 스토어 (빌드 시 생성)
│   ├── products/
│   │   └── index.faiss
│   ├── tone/
│   │   └── index.faiss
│   └── reviews/
│       └── index.faiss
├── api/                          # Vercel serverless API 핸들러
│   └── index.py
├── static/                       # 웹 데모 정적 파일
│   ├── index.html
│   ├── script.js
│   └── style.css
├── app.py
├── demo.py
├── quickstart.py
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
# 입력: 모든 수집된 컨텍스트
# 처리: Google Gemini (예: `models/gemini-2.5-flash`)으로 제목+본문 생성
# 출력: 제목 (40자 이내), 본문 (350자 이내)

### 7. Quality Validator (품질 검증)
- 입력: 생성된 메시지
- 처리: 길이 제한, 금칙어, 톤 일관성 체크
- 출력: 검증 통과 여부, 이슈 목록

## 기술 스택

- **LangChain**: LLM 통합 및 체인 구성
- **LangGraph**: 상태 기반 워크플로우 관리
- **Google Gemini**: 메시지 생성 LLM (예: `models/gemini-2.5-flash`)
- **Google Generative Embeddings**: `models/text-embedding-004`
- **FAISS**: 벡터 유사도 검색
- **Pandas**: 데이터 처리
- **Python-dotenv**: 환경 변수 관리

## 환경 변수 설정

`.env` 파일에서 다음 항목을 설정할 수 있습니다:

```bash
# Google Gemini API 키 (필수)
GOOGLE_API_KEY=your-google-api-key-here

# 모델 설정
# 권장: models/gemini-2.5-flash (생성), 임베딩은 models/text-embedding-004
MODEL_NAME=models/gemini-2.5-flash
EMBEDDING_MODEL=models/text-embedding-004
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

## 트러블슈팅

### 1. 벡터 스토어가 생성되지 않는 경우

```python
# 벡터 스토어 강제 재생성
agent = MarketingMessageAgent(db_path="./brands_db")
agent.vector_manager.build_all_stores()
```

### 2. Google API 오류

- `.env` 파일에 올바른 `GOOGLE_API_KEY`가 설정되어 있는지 확인
- API 사용량 한도를 초과하지 않았는지 확인

### 3. 인코딩 오류 (Windows)

- CSV 파일은 모두 UTF-8-sig로 인코딩됨
- 콘솔 출력이 깨지는 경우, 이는 Windows 콘솔의 cp949 인코딩 제한이며 데이터 자체는 정상

## 라이센스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.
