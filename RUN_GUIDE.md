# 실행 가이드

실제 데이터 구조로 변경된 시스템을 실행하는 방법입니다.

## 1. 사전 준비

### 환경 변수 설정

```bash
# .env 파일 생성 (아직 없다면)
cp .env.example .env

# .env 파일 편집하여 Google API Key 입력
# GOOGLE_API_KEY=your-google-api-key-here
```

### 필수 패키지 설치

```bash
pip install -r requirements.txt
```

## 2. 벡터 스토어 빌드 (최초 1회 필수)

새로운 데이터 구조로 벡터 스토어를 구축해야 합니다.

```bash
# 기존 벡터 스토어 삭제 (있다면)
rm -rf ./vector_store

# 벡터 스토어 빌드
python3 << 'EOF'
from src.embeddings import VectorStoreManager

print("벡터 스토어 빌드 시작...")
manager = VectorStoreManager(db_path="./brands_db", vector_path="./vector_store")
manager.build_all_stores()
print("✓ 벡터 스토어 빌드 완료!")
EOF
```

**예상 소요 시간**: 1-3분 (데이터 양과 네트워크 속도에 따라 다름)

## 3. 시스템 실행

### 옵션 1: 간단한 테스트 (quickstart.py)

```bash
python quickstart.py
```

가장 간단하게 메시지 생성을 테스트할 수 있습니다.

### 옵션 2: 데모 실행 (demo.py)

```bash
python demo.py
```

다양한 시나리오로 메시지 생성을 테스트합니다.

### 옵션 3: 웹 애플리케이션 (app.py)

```bash
python app.py
```

Flask 웹 서버가 실행됩니다.
- 기본 포트: 5000
- 접속 URL: http://localhost:5000

### 옵션 4: Vercel 배포용 API (api/index.py)

Vercel에 배포하려면:

```bash
# Vercel CLI 설치 (없다면)
npm install -g vercel

# 배포
vercel deploy
```

## 4. 테스트 실행

```bash
# 단위 테스트
python -m pytest tests/ -v

# 특정 테스트만 실행
python -m pytest tests/test_generator.py -v
```

## 5. 벡터 스토어 재빌드가 필요한 경우

다음 경우에 벡터 스토어를 재빌드해야 합니다:

- 데이터 파일 변경 (all_products.csv, all_reviews.csv, marketing_tone_info.xlsx)
- 임베딩 모델 변경
- 데이터 구조 변경

```bash
# 벡터 스토어 삭제 후 재빌드
rm -rf ./vector_store
python3 -c "from src.embeddings import VectorStoreManager; VectorStoreManager().build_all_stores()"
```

## 6. 실제 데이터 적용 시

샘플 데이터를 실제 데이터로 교체할 때:

```bash
# 1. 실제 데이터 파일 준비
# - brands_db/products_db/all_products.csv
# - brands_db/reviews_db/all_reviews.csv
# - brands_db/brand_tone_corpus/marketing_tone_info.xlsx

# 2. 벡터 스토어 재빌드
rm -rf ./vector_store
python3 -c "from src.embeddings import VectorStoreManager; VectorStoreManager().build_all_stores()"

# 3. 시스템 실행
python quickstart.py  # 또는 demo.py, app.py
```

## 트러블슈팅

### 문제: ModuleNotFoundError

```bash
# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

### 문제: Google API Key 에러

```bash
# .env 파일 확인
cat .env | grep GOOGLE_API_KEY

# API Key가 올바른지 확인
# https://aistudio.google.com/app/apikey
```

### 문제: 벡터 스토어 로딩 실패

```bash
# 벡터 스토어 재빌드
rm -rf ./vector_store
python3 -c "from src.embeddings import VectorStoreManager; VectorStoreManager().build_all_stores()"
```

### 문제: CSV 파일을 찾을 수 없음

```bash
# 데이터 파일 존재 확인
ls brands_db/products_db/all_products.csv
ls brands_db/reviews_db/all_reviews.csv
ls brands_db/brand_tone_corpus/marketing_tone_info.xlsx

# 파일이 없다면 샘플 데이터 재생성
python3 << 'EOF'
import pandas as pd
import random
from pathlib import Path

# (샘플 데이터 생성 코드)
# DATA_STRUCTURE.md 참고
EOF
```

## 데이터 구조

데이터 구조에 대한 자세한 정보는 `DATA_STRUCTURE.md` 파일을 참고하세요.

```bash
cat DATA_STRUCTURE.md
```
