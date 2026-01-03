# 시스템 실행 가이드 (초보자용)

이 가이드는 처음 시스템을 실행하는 분들을 위한 상세한 단계별 설명입니다.

## 📍 Step 0: 현재 위치 확인

### Windows 사용자
1. **명령 프롬프트** 또는 **PowerShell** 열기
   - `Win + R` 키 → `cmd` 입력 → Enter
   - 또는 시작 메뉴에서 "cmd" 검색

2. 프로젝트 폴더로 이동
   ```cmd
   cd C:\Users\YourName\amore_contest
   ```
   (실제 프로젝트가 있는 경로로 변경하세요)

### Mac/Linux 사용자
1. **터미널** 열기
   - Mac: `Command + Space` → "터미널" 검색
   - Linux: `Ctrl + Alt + T`

2. 프로젝트 폴더로 이동
   ```bash
   cd ~/amore_contest
   ```
   또는
   ```bash
   cd /path/to/your/amore_contest
   ```

### 현재 위치 확인 방법
```bash
pwd  # Mac/Linux
cd   # Windows

# 결과 예시: /home/user/amore_contest
```

## 📦 Step 1: 환경 설정

### 1-1. Python 설치 확인

먼저 Python이 설치되어 있는지 확인합니다.

```bash
python3 --version
```

또는 (Windows)

```cmd
python --version
```

**예상 출력**: `Python 3.8.0` 이상이어야 합니다.

> ⚠️ Python이 없다면: https://www.python.org/downloads/ 에서 설치

### 1-2. 필요한 패키지 설치

프로젝트 폴더에서 다음 명령어를 실행합니다.

```bash
pip install -r requirements.txt
```

**예상 출력**:
```
Collecting langchain>=0.1.0
Downloading langchain-...
Successfully installed langchain-... faiss-cpu-... pandas-...
```

소요 시간: 약 2-5분

### 1-3. 환경 변수 파일 생성

#### Option A: 직접 생성 (추천)

1. 프로젝트 폴더에 `.env` 파일을 새로 만듭니다
2. 아래 내용을 복사해서 붙여넣습니다:

```env
# Google Gemini API Key
GOOGLE_API_KEY=여기에_실제_API_키_입력

# Model Configuration
# 권장: models/gemini-2.5-flash, 임베딩은 models/text-embedding-004
MODEL_NAME=models/gemini-2.5-flash
EMBEDDING_MODEL=models/text-embedding-004

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Message Generation Settings
MAX_TITLE_LENGTH=40
MAX_BODY_LENGTH=350
TEMPERATURE=0.7

# Database Paths
BRANDS_DB_PATH=./brands_db
CUSTOMERS_DB_PATH=./customers_db
VECTOR_STORE_PATH=./vector_store

# Logging
LOG_LEVEL=INFO
```

#### Option B: 예제 파일 복사

```bash
# Mac/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

3. `.env` 파일을 텍스트 에디터로 열어서 `GOOGLE_API_KEY` 값을 수정합니다

### 1-4. Google API Key 발급받기

1. https://aistudio.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. **"Create API Key"** 버튼 클릭
4. 생성된 API Key를 복사
5. `.env` 파일의 `GOOGLE_API_KEY=` 뒤에 붙여넣기

**예시**:
```
GOOGLE_API_KEY=AIzaSyABC123def456GHI789jkl012MNO345pqr
```

## 🔨 Step 2: 벡터 스토어 빌드 (최초 1회 필수)

### 2-1. 기존 벡터 스토어 삭제 (있다면)

```bash
# Mac/Linux
rm -rf ./vector_store

# Windows
rmdir /s /q vector_store
```

에러가 나도 괜찮습니다 (폴더가 없어서 나는 에러).

### 2-2. 벡터 스토어 빌드 실행

프로젝트 폴더에서 아래 명령어를 **한 줄씩** 복사해서 실행합니다.

#### Mac/Linux:

```bash
python3 << 'EOF'
from src.embeddings import VectorStoreManager

print("벡터 스토어 빌드 시작...")
manager = VectorStoreManager(db_path="./brands_db", vector_path="./vector_store")
manager.build_all_stores()
print("✓ 벡터 스토어 빌드 완료!")
EOF
```

#### Windows (방법 1 - 추천):

1. 메모장을 열고 아래 내용을 붙여넣습니다:

```python
from src.embeddings import VectorStoreManager

print("벡터 스토어 빌드 시작...")
manager = VectorStoreManager(db_path="./brands_db", vector_path="./vector_store")
manager.build_all_stores()
print("✓ 벡터 스토어 빌드 완료!")
```

2. 파일을 `build_vector_store.py`로 저장
3. 명령 프롬프트에서 실행:

```cmd
python build_vector_store.py
```

#### Windows (방법 2):

명령 프롬프트에서 한 줄로 실행:

```cmd
python -c "from src.embeddings import VectorStoreManager; manager = VectorStoreManager(); manager.build_all_stores()"
```

### 2-3. 빌드 진행 확인

**예상 출력**:
```
벡터 스토어 빌드 시작...
[Vector Store] 벡터 스토어 구축 시작...
  - 제품 데이터 임베딩 중...
  - 브랜드 톤 데이터 임베딩 중...
  - 리뷰 데이터 임베딩 중...
  - 벡터 스토어 저장 중...
[Vector Store] 모든 벡터 스토어 구축 완료!
✓ 벡터 스토어 빌드 완료!
```

**소요 시간**: 약 1-3분

> ⚠️ 에러 발생 시:
> - `ModuleNotFoundError`: Step 1-2 (패키지 설치) 다시 실행
> - `GOOGLE_API_KEY error`: Step 1-4 (API Key 설정) 확인
> - `FileNotFoundError`: 현재 폴더 위치 확인 (`pwd` 또는 `cd`)

## 🚀 Step 3: 시스템 실행

이제 3가지 방법 중 하나를 선택해서 실행할 수 있습니다.

### 방법 1: 간단한 테스트 (quickstart.py)

**가장 간단한 테스트**입니다. 한 명의 고객에 대한 메시지를 생성합니다.

```bash
python quickstart.py
```

**예상 출력**:
```
[1. Persona Analyzer] 페르소나 분석 중...
  [OK] 핵심 니즈: ['건조 개선', '수분 공급']
[2. Brand Selector] 브랜드 선택 중...
  [OK] 선택된 브랜드: 라네즈
...
[7. Quality Validator] 품질 검증 중...
  [OK] 검증 통과!

=== 생성된 메시지 ===
제목: 건조한 피부를 위한 라네즈 수분 케어
본문: 안녕하세요 김지현님! 요즘 날씨가 건조해서...
```

### 방법 2: 데모 실행 (demo.py)

**여러 시나리오를 테스트**합니다. 다양한 고객/브랜드 조합으로 메시지를 생성합니다.

```bash
python demo.py
```

**예상 출력**:
```
=== 아모레퍼시픽 CRM 마케팅 메시지 생성기 데모 ===

--- 데모 1: 20대 건성 피부 고객 (에뛰드) ---
...

--- 데모 2: 30대 지성 피부 고객 (라네즈) ---
...

(총 5개 데모 실행)
```

### 방법 3: 웹 서버 실행 (app.py)

**웹 브라우저에서 사용**할 수 있습니다.

```bash
python app.py
```

**예상 출력**:
```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
Press CTRL+C to quit
```

이제 웹 브라우저를 열고 다음 주소로 접속:
- http://localhost:5000

서버를 종료하려면 터미널에서 `Ctrl + C` 누르기

## 📊 Step 4: 결과 확인

### 성공 여부 확인 방법

#### ✅ 성공한 경우:
- 에러 메시지 없이 진행됨
- `[OK]` 메시지가 보임
- 제목과 본문이 생성됨
- `[✓]` 또는 `통과` 메시지가 보임

#### ❌ 실패한 경우:
- `[ERROR]` 또는 `[FAIL]` 메시지
- Python 에러 메시지 (Traceback)

## 🔧 문제 해결

### 자주 발생하는 문제

#### 1. `ModuleNotFoundError: No module named 'langchain'`

**원인**: 필요한 패키지가 설치되지 않음

**해결**:
```bash
pip install -r requirements.txt
```

#### 2. `API key not valid`

**원인**: Google API Key가 잘못되었거나 설정되지 않음

**해결**:
1. `.env` 파일 확인
2. API Key 다시 발급: https://aistudio.google.com/app/apikey
3. `.env` 파일에 올바른 키 입력

#### 3. `FileNotFoundError: all_products.csv`

**원인**: 현재 폴더가 프로젝트 루트가 아님

**해결**:
```bash
# 현재 위치 확인
pwd  # Mac/Linux
cd   # Windows

# 프로젝트 폴더로 이동
cd /path/to/amore_contest
```

#### 4. `vector_store 폴더를 찾을 수 없음`

**원인**: 벡터 스토어를 빌드하지 않음

**해결**: Step 2 (벡터 스토어 빌드) 다시 실행

## 📂 폴더 구조 확인

정상적으로 설정되었다면 아래와 같은 구조여야 합니다:

```
amore_contest/
├── .env                    ← API Key가 들어있는 파일
├── brands_db/
│   ├── products_db/
│   │   └── all_products.csv
│   ├── reviews_db/
│   │   └── all_reviews.csv
│   └── brand_tone_corpus/
│       └── marketing_tone_info.xlsx
├── vector_store/           ← 빌드 후 생성됨
│   ├── products/
│   ├── reviews/
│   └── tone/
├── src/
│   └── embeddings.py
├── quickstart.py
├── demo.py
└── app.py
```

폴더 구조 확인 방법:

```bash
# Mac/Linux
ls -la

# Windows
dir
```

## 💡 추가 도움말

### Q: 어떤 파일을 먼저 실행해야 하나요?
A: `quickstart.py`가 가장 간단합니다.

### Q: 매번 벡터 스토어를 빌드해야 하나요?
A: 아니요. 최초 1회만 빌드하면 됩니다. 데이터가 변경될 때만 다시 빌드합니다.

### Q: 웹 서버를 어떻게 종료하나요?
A: 터미널에서 `Ctrl + C` 키를 누르세요.

### Q: API 사용료가 발생하나요?
A: Google Gemini API는 무료 할당량이 있습니다. 일반적인 테스트는 무료 범위 내입니다.

## 🎯 다음 단계

시스템이 정상 작동하면:

1. **실제 데이터 준비**
   - `all_products.csv`를 실제 제품 데이터로 교체
   - `all_reviews.csv`를 실제 리뷰 데이터로 교체

2. **벡터 스토어 재빌드**
   ```bash
   rm -rf ./vector_store
   python build_vector_store.py
   ```

3. **시스템 테스트**
   ```bash
   python demo.py
   ```

## 📞 지원

문제가 계속되면:
- `DATA_STRUCTURE.md`: 데이터 구조 상세 설명
- `RUN_GUIDE.md`: 고급 실행 가이드
- GitHub Issues: 버그 리포트 및 질문
