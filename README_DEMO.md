# 아모레퍼시픽 CRM 메시지 생성기 - 웹 데모

> 고객 맞춤형 CRM 마케팅 메시지를 자동으로 생성하는 웹 애플리케이션

![Demo Screenshot](https://via.placeholder.com/800x400/A8C5F0/FFFFFF?text=Amorepacific+CRM+Message+Generator)

## ✨ 주요 기능

- **직관적인 페르소나 입력**: 드롭다운, 체크박스 등 쉬운 UI로 고객 정보 입력
- **실시간 메시지 생성**: AI 기반으로 브랜드별 맞춤 메시지 자동 생성
- **5개 브랜드 지원**: 에뛰드, 라네즈, 헤라, 설화수, 아이오페
- **모던한 UI/UX**: 블루 그라데이션 + 크리스탈 느낌의 깔끔한 디자인

## 🎨 디자인 특징

- **컬러 팔레트**: #A8C5F0 → #C8D5F0 블루 그라데이션
- **유리 효과**: Glassmorphism 디자인 (backdrop-filter, 반투명 효과)
- **반응형**: 모바일, 태블릿, 데스크톱 모두 지원

## 🚀 빠른 시작

### 로컬 실행

```bash
# 1. 저장소 클론
git clone https://github.com/stxllaaa/amore_contest.git
cd amore_contest

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일에 GOOGLE_API_KEY 입력

# 5. 서버 실행
python app.py
```

브라우저에서 `http://localhost:5000` 접속

### Vercel 배포

자세한 배포 방법은 [DEPLOY.md](DEPLOY.md) 참조

**간단 배포:**

```bash
# Vercel CLI 설치
npm install -g vercel

# 배포
vercel

# 환경 변수 설정
vercel env add GOOGLE_API_KEY

# 프로덕션 배포
vercel --prod
```

## 📝 사용 방법

### 1. 고객 정보 입력

왼쪽 폼에서 다음 정보를 입력하세요:

- **나이대**: 10대 ~ 50대
- **직업**: 대학생, 직장인, 전문직 등
- **피부 타입**: 건성, 지성, 복합성, 민감성, 중성
- **피부 고민**: 모공, 피지, 건조, 주름 등 (복수 선택 가능)
- **관심 제품 카테고리**: 스킨케어, 베이스 메이크업 등
- **선호 브랜드**: 에뛰드, 라네즈, 헤라, 설화수, 아이오페

### 2. 메시지 생성

"메시지 생성하기" 버튼을 클릭하면 AI가 자동으로:

- 브랜드에 맞는 톤앤매너로 메시지 작성
- 고객 페르소나에 최적화된 제품 3개 추천
- 제목(40자 이내) + 본문(350자 이내) 생성

### 3. 결과 확인

오른쪽 영역에서 생성된 메시지를 확인할 수 있습니다:

- 제목
- 본문
- 추천 제품 목록

## 🏗️ 기술 스택

### Backend
- **Flask**: 웹 프레임워크
- **LangChain**: LLM 통합
- **LangGraph**: 워크플로우 관리
- **Google Gemini**: AI 모델 (e.g. `models/gemini-2.5-flash`)
- **FAISS**: 벡터 검색

### Frontend
- **HTML5**: 시맨틱 마크업
- **CSS3**: Glassmorphism, Flexbox, Grid
- **Vanilla JavaScript**: API 통신, DOM 조작

### DevOps
- **Vercel**: 서버리스 배포
- **Git**: 버전 관리

## 📂 프로젝트 구조

```
amore_contest/
├── api/
│   └── index.py              # Flask 앱 (Vercel Serverless Function)
├── static/
│   ├── index.html            # 메인 페이지
│   ├── style.css             # 스타일시트
│   └── script.js             # 클라이언트 스크립트
├── src/
│   ├── message_generator.py  # 메시지 생성 에이전트
│   ├── graph_nodes.py        # LangGraph 노드
│   ├── graph_builder.py      # 워크플로우 빌더
│   ├── embeddings.py         # 벡터 스토어 관리
│   └── prompts.py            # 프롬프트 템플릿
├── brands_db/                # 브랜드 데이터
│   ├── brand_info.csv
│   ├── products_db/          # 제품 정보 (75개)
│   ├── brand_tone_corpus/    # 브랜드 톤 예시 (75개)
│   └── reviews_db/           # 리뷰 데이터 (180개)
├── app.py                    # 로컬 개발용 서버
├── vercel.json               # Vercel 배포 설정
├── requirements.txt          # Python 패키지
├── DEPLOY.md                 # 배포 가이드
└── README_DEMO.md            # 이 파일
```

## 🎯 주요 변경사항 (기존 프로젝트 대비)

### ✅ 추가된 기능

1. **웹 UI**: CLI에서 웹 인터페이스로 전환
2. **폼 기반 입력**: CSV 대신 사용자가 직접 입력
3. **실시간 생성**: 브라우저에서 즉시 메시지 생성
4. **Vercel 배포**: 서버리스 배포 지원

### ❌ 제거된 기능

1. **평가 시스템**: evaluation 폴더 전체 제거
2. **CSV 페르소나**: customer_personas.csv 의존성 제거
3. **CLI 데모**: demo.py 유지 (기존 사용자용)

### 🔄 유지된 기능

1. **LangGraph 워크플로우**: 7단계 메시지 생성 파이프라인
2. **RAG 기반 검색**: 제품, 리뷰, 톤 벡터 검색
3. **브랜드별 톤앤매너**: 5개 브랜드 고유 스타일
4. **품질 검증**: 제목/본문 길이, 금칙어 체크

## 🔐 환경 변수

`.env` 파일에 다음 변수 설정:

```bash
# Google Gemini API (필수)
GOOGLE_API_KEY=your-api-key-here

# 모델 설정 (선택)
MODEL_NAME=models/gemini-2.5-flash
EMBEDDING_MODEL=models/text-embedding-004
TEMPERATURE=0.7

# 경로 설정 (선택)
BRANDS_DB_PATH=./brands_db
VECTOR_STORE_PATH=./vector_store

# 메시지 제약 (선택)
MAX_TITLE_LENGTH=40
MAX_BODY_LENGTH=350
```

## 📊 API 엔드포인트

### `POST /api/generate`

메시지 생성 요청

**요청:**
```json
{
  "age": 27,
  "occupation": "회사원",
  "skin_type": "복합성",
  "skin_concerns": "모공, 피지",
  "product_category": "스킨케어",
  "preferred_brand": "라네즈",
  "message_purpose": "personalized"
}
```

**응답:**
```json
{
  "success": true,
  "result": {
    "title": "당신의 피부를 위한 특별한 선택",
    "body": "...",
    "products": ["라네즈 워터뱅크 에센스", "..."],
    "brand": "라네즈",
    "is_valid": true
  }
}
```

### `GET /api/brands`

브랜드 목록 조회

## 🐛 문제 해결

### 1. 메시지 생성이 느려요

- **원인**: Cold Start (첫 요청 시 벡터 스토어 로딩)
- **해결**: 2번째 요청부터는 빨라집니다

### 2. API 에러가 발생해요

- **원인**: Google API 키 미설정 또는 만료
- **해결**: `.env` 파일에 올바른 API 키 입력

### 3. Vercel 배포 시 타임아웃

- **원인**: Serverless Function 기본 타임아웃 10초
- **해결**: Vercel Pro 플랜 사용 (60초 타임아웃)

## 📈 성능 최적화

1. **벡터 스토어 캐싱**: 에이전트 싱글톤 패턴
2. **API 응답 최적화**: 필요한 데이터만 전송
3. **프론트엔드 최적화**: Vanilla JS로 경량화

## 📄 라이센스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 👥 기여자

- [stxllaaa](https://github.com/stxllaaa)

## 🔗 관련 링크

- [원본 프로젝트 README](README.md)
- [배포 가이드](DEPLOY.md)
- [Vercel 문서](https://vercel.com/docs)
- [Flask 문서](https://flask.palletsprojects.com/)

---

**Made with ❤️ for Amorepacific CRM**
