# 실제 데이터 구조 변경사항

이 문서는 실제 운영 데이터 구조에 맞춰 시스템을 수정한 내용을 설명합니다.

## 변경 개요

기존에는 브랜드별/제품별로 개별 CSV 파일을 사용했으나, 실제 데이터 구조에 맞춰 **통합 CSV 파일** 구조로 변경했습니다.

## 데이터 구조

### 1. products_db (제품 데이터베이스)

**파일**: `brands_db/products_db/all_products.csv`

**컬럼 구조**:
```
product_id      : 제품 고유 ID (예: etude_skin_1)
category        : 제품 카테고리 (skin, eye, lip, base 등)
brand           : 브랜드명 (etude, laneige, sulwhasoo, iope, hera 등)
product_name    : 제품명
review_count    : 리뷰 수
price           : 가격
main_ingredients: 주요 성분
top_good_keywords: 긍정 키워드 Top-K (쉼표로 구분)
top_bad_keywords : 부정 키워드 Top-K (쉼표로 구분)
```

**예시**:
```csv
product_id,category,brand,product_name,review_count,price,main_ingredients,top_good_keywords,top_bad_keywords
etude_skin_1,skin,etude,수분가득 콜라겐 시트 마스크 25ml,504,2500,정제수·하이드롤라이즈드콜라겐·부틸렌글라이콜...,촉촉해요·발색좋아요·가성비·순해요,건조해요·발색약해요·비싸요
```

### 2. reviews_db (리뷰 데이터베이스)

**파일**: `brands_db/reviews_db/all_reviews.csv`

**컬럼 구조**:
```
product_id    : 제품 ID (products_db와 연결)
brand         : 브랜드명
review_id     : 리뷰 고유 ID
gender        : 성별 (남성/여성)
age_group     : 연령대 (10대, 20대, 30대, 40대, 50대)
skin_type     : 피부 타입 (건성, 지성, 복합성, 민감성, 수분부족지성)
skin_concerns : 피부 고민 (트러블, 칙칙함, 모공, 주름 등)
attr1_name    : 속성1 이름 (예: 보습감)
attr1_value   : 속성1 값 (예: 촉촉해요)
attr2_name    : 속성2 이름 (예: 향)
attr2_value   : 속성2 값 (예: 향이 좋아요)
attr3_name    : 속성3 이름 (예: 민감성)
attr3_value   : 속성3 값 (예: 순해서 좋아요)
review_text   : 리뷰 본문
category      : 제품 카테고리
good          : 긍정 키워드 리스트 (쉼표로 구분)
bad           : 부정 키워드 리스트 (쉼표로 구분)
lifestyle     : 라이프스타일 키워드 (사용 맥락, 개인 특성)
```

**예시**:
```csv
product_id,brand,review_id,gender,age_group,skin_type,skin_concerns,attr1_name,attr1_value,attr2_name,attr2_value,attr3_name,attr3_value,review_text,category,good,bad,lifestyle
etude_skin_1,etude,dusc****,남성,30대,지성,트러블,보습감,촉촉해요,향,향이 좋아요,민감성,순해서 좋아요,요즘 날씨가 너무 더워서 피부에 열감이 있어 구매하게되었습니다...,skin,촉촉해요·발색좋아요·가성비,건조해요·비싸요,학교·데일리·학생
```

### 3. brand_tone_corpus (브랜드 톤 코퍼스)

**파일**: `brands_db/brand_tone_corpus/marketing_tone_info.xlsx`

**컬럼 구조**:
```
brand      : 브랜드명 (etude, laneige, sulwhasoo, iope, hera)
platform   : 플랫폼 (instagram, facebook, blog 등)
tone_text  : 마케팅 메시지 원문
```

**예시**:
```
brand: etude
platform: instagram
tone_text: "눈썹 그리기 어려운 사람 집중!!!୧(•̀ө•́)୨
더욱더 섬세하게 눈썹 메이크오버 할 수 있는
컨트롤 슬라이드 삼면 브로우🤎🩶🖤..."
```

## 주요 변경사항

### 1. embeddings.py

- **_build_products_store()**: 브랜드별 개별 CSV → `all_products.csv` 통합 파일 사용
- **_build_tone_store()**: 브랜드별 CSV → `marketing_tone_info.xlsx` 사용
- **_build_reviews_store()**: 제품별 개별 CSV → `all_reviews.csv` 통합 파일 사용

### 2. 데이터 필터링

- **products_db**: 모든 제품 데이터를 브랜드 구분 없이 하나의 파일에서 관리
- **reviews_db**: `lifestyle` 컬럼이 있는 리뷰만 벡터 스토어에 포함
- **brand_tone_corpus**: 실제 수집된 마케팅 메시지 데이터 사용

## 기대 효과

1. **데이터 관리 효율성**: 브랜드별로 개별 파일을 관리하지 않고 통합 파일로 관리
2. **확장성**: 새로운 브랜드 추가 시 파일 추가 없이 데이터만 추가
3. **실제 운영 환경 반영**: 실제 데이터 수집/분석 파이프라인과 동일한 구조
4. **키워드 기반 추천**: good/bad 키워드를 활용한 제품 추천 가능

## 마이그레이션 가이드

기존 개별 CSV 파일 구조에서 통합 구조로 마이그레이션하려면:

1. 기존 벡터 스토어 삭제
   ```bash
   rm -rf ./vector_store
   ```

2. 통합 데이터 파일 준비
   - `brands_db/products_db/all_products.csv`
   - `brands_db/reviews_db/all_reviews.csv`
   - `brands_db/brand_tone_corpus/marketing_tone_info.xlsx`

3. 벡터 스토어 재구축
   ```python
   from src.embeddings import VectorStoreManager

   manager = VectorStoreManager()
   manager.build_all_stores()
   ```

## 주의사항

- **brand_tone_corpus**: `marketing_tone_info.xlsx`가 실제 데이터이므로 가짜 데이터를 생성하지 않음
- **top_good_keywords, top_bad_keywords**: 현재는 샘플 데이터이며, 실제 데이터 분석 완료 시 업데이트 예정
- **lifestyle 키워드**: 사용자 리뷰 기반으로 추출한 맥락 정보로, RAG 검색 시 활용됨
