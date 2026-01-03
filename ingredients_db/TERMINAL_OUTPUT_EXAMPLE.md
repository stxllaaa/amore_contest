# 터미널에서 성분 추천 프로세스 확인하기

성분 DB 통합 후, 터미널에서 성분이 어떻게 추천되는지 상세한 로그를 확인할 수 있습니다.

## 🚀 테스트 방법

### 방법 1: 테스트 스크립트 실행 (가장 간단)

```bash
# 1. 성분 DB 생성 (아직 안 했다면)
python ingredients_db/build_ingredients_db.py

# 2. 테스트 스크립트 실행
python test_ingredients_recommendation.py
```

### 방법 2: 웹 서버 실행 후 확인

```bash
# 웹 서버 실행
python app.py
```

브라우저에서 메시지를 생성하면, 터미널에 상세 로그가 출력됩니다.

## 📊 터미널 출력 예시

성분 DB가 정상적으로 통합되면 다음과 같은 로그를 볼 수 있습니다:

```
============================================================
메시지 생성 시작
- 페르소나: custom
- 목적: personalized
- 브랜드: 자동 선택
============================================================

[1. Persona Analyzer] 페르소나 분석 중...
  [OK] 핵심 니즈: ['건조', '주름']

[2. Brand Selector] 브랜드 선택 중...
  [OK] 선택된 브랜드: 라네즈

[3. Product Retriever] 제품 및 성분 검색 중...
  [OK] 검색된 제품: 3개
  [성분 검색 쿼리] 건조, 주름 개선, 건조, 주름

  ┌─── 추천 성분 목록 ───
  │ [1] 히알루론산 (Hyaluronic Acid)
  │     효능: Hydration, plumping, anti-aging
  │     피부고민: 건조, 주름
  │
  │ [2] 세라마이드 (Ceramides)
  │     효능: Barrier repair, moisture retention
  │     피부고민: 건조
  │
  │ [3] 레티놀 (Retinol)
  │     효능: Anti-aging, cell turnover, collagen production
  │     피부고민: 주름
  │
  │ [4] 펩타이드 (Peptides)
  │     효능: Anti-aging, firmness, collagen production
  │     피부고민: 주름, 탄력저하
  │
  │ [5] 나이아신아마이드 (Niacinamide)
  │     효능: Brightening, pore minimizing, oil control
  │     피부고민: 칙칙함, 모공
  │
  └─────────────────────
  [OK] 총 5개 성분 추천됨

[4. Review Context Enricher] 리뷰 분석 중...
  [OK] 공감 포인트: ['직장생활', '시간부족']

[5. Tone Adapter] 톤 예시 검색 중...
  [OK] 톤 예시: 3개

[6. Message Generator] 메시지 생성 중...

  [메시지에 포함될 성분]
    1. 히알루론산 - Hydration, plumping, anti-aging...
    2. 세라마이드 - Barrier repair, moisture retention...
    3. 레티놀 - Anti-aging, cell turnover, collagen production...

  [OK] 제목: 당신의 피부를 위한 특별한 솔루션...

[7. Quality Validator] 품질 검증 중...
  [OK] 검증 통과!

============================================================
메시지 생성 완료!
============================================================
```

## 🔍 주요 로그 포인트

### 1. 성분 검색 쿼리
```
[성분 검색 쿼리] 건조, 주름 개선, 건조, 주름
```
- 피부 고민 기반으로 성분 검색 쿼리 생성
- 사용자 입력 → 벡터 검색 쿼리 변환

### 2. 추천 성분 목록 (상세)
```
┌─── 추천 성분 목록 ───
│ [1] 히알루론산 (Hyaluronic Acid)
│     효능: Hydration, plumping, anti-aging
│     피부고민: 건조, 주름
│
│ [2] 세라마이드 (Ceramides)
...
└─────────────────────
```
- **총 5개 성분** 검색됨
- 각 성분의 **한글명**, **영문명**, **효능**, **관련 피부고민** 출력
- 박스 형태로 시각적으로 보기 쉽게 표시

### 3. 메시지에 포함될 성분 (최종 선택)
```
[메시지에 포함될 성분]
  1. 히알루론산 - Hydration, plumping, anti-aging...
  2. 세라마이드 - Barrier repair, moisture retention...
  3. 레티놀 - Anti-aging, cell turnover, collagen production...
```
- **상위 3개 성분**만 메시지에 포함
- 실제로 LLM 프롬프트에 전달되는 성분

## 🎯 성분이 없는 경우

성분 DB가 없거나 검색 결과가 없으면:

```
[3. Product Retriever] 제품 및 성분 검색 중...
  [OK] 검색된 제품: 3개
  [성분 검색 쿼리] 건조, 주름 개선, 건조, 주름
  [참고] 성분 DB 없음 (성분 검색 건너뜀)

...

[6. Message Generator] 메시지 생성 중...
  [참고] 성분 정보 없음 (기본 메시지 생성)
```

- 시스템은 정상 작동
- 제품 정보만으로 메시지 생성

## 💡 활용 팁

### 1. 성분 매칭 확인

다양한 피부 고민으로 테스트:

```python
# 건조 → 히알루론산, 세라마이드
skin_concerns = '건조'

# 주름 → 레티놀, 펩타이드
skin_concerns = '주름'

# 모공 → 나이아신아마이드, AHA/BHA
skin_concerns = '모공, 피지'

# 민감함 → 센텔라, 녹차 추출물
skin_concerns = '민감함, 자극'
```

### 2. 로그 저장

터미널 출력을 파일로 저장:

```bash
python test_ingredients_recommendation.py > output.log 2>&1
cat output.log
```

### 3. 실시간 모니터링

웹 서버 실행 시:

```bash
python app.py | grep "성분"
```

성분 관련 로그만 필터링해서 확인

## 🐛 문제 해결

### 성분이 검색되지 않는 경우

```
[참고] 성분 DB 없음 (성분 검색 건너뜀)
```

**원인**:
1. 성분 DB가 생성되지 않음
2. 벡터 스토어가 재생성되지 않음

**해결**:
```bash
# 1. 성분 DB 생성
python ingredients_db/build_ingredients_db.py

# 2. 벡터 스토어 재생성
rm -rf vector_store/

# 3. 다시 실행
python app.py
```

### 성분이 검색되지만 메시지에 반영 안 됨

프롬프트 확인이 필요할 수 있습니다.
`src/graph_nodes.py`의 `message_generator` 함수에서
성분 정보가 프롬프트에 추가되는지 확인하세요.

## 📈 기대 결과

성분 DB가 정상적으로 통합되면:

✅ 터미널에 **5개 추천 성분** 표시
✅ **상위 3개 성분**이 메시지에 포함됨
✅ 메시지에 **성분 효능** 자연스럽게 녹아들어감

예시:
> "라네즈 워터뱅크 에센스는 **히알루론산**이 피부 깊숙이 수분을 공급하고,
> **세라마이드**가 피부 장벽을 강화해 촉촉함을 오래 유지시켜줍니다."
