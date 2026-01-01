# 평가 시스템 사용 가이드

## 빠른 시작

### 1분 샘플 테스트 (시스템 동작 확인)

```bash
python evaluation/sample_evaluation.py
```

**실행 내용:**
- 2개 샘플 메시지 생성 및 평가
- 시스템 정상 동작 확인

**예상 소요 시간:** 약 1-2분

### 전체 평가 (40개 조합)

```bash
python run_evaluation.py
```

**실행 내용:**
- 8명 페르소나 × 5가지 메시지 목적 = 40개 조합 테스트
- 각 메시지 LLM 평가 (4가지 기준)
- CSV 결과 저장
- 8가지 시각화 차트 생성

**예상 소요 시간:** 약 20-30분

## 개별 실행

### 테스트만 실행

```bash
python evaluation/test_all_combinations.py
```

**출력:**
- `evaluation/results/test_results_YYYYMMDD_HHMMSS.csv`
- 콘솔 요약 통계

### 시각화만 실행 (기존 CSV 사용)

```bash
python evaluation/visualize_results.py
```

**출력:**
- `evaluation/plots/*.png` (8개 차트)

## 평가 지표 해석

### 점수 기준 (1-5점)

| 점수 | 평가 | 조치 |
|------|------|------|
| 4.5-5.0 | 우수 | 즉시 사용 가능 |
| 3.5-4.4 | 양호 | 소폭 수정 후 사용 |
| 2.5-3.4 | 보통 | 개선 필요 |
| 1.5-2.4 | 미흡 | 재생성 권장 |
| 1.0-1.4 | 불량 | 재생성 필수 |

### 4가지 평가 기준

1. **브랜드 톤 적합성**
   - 브랜드 고유의 톤앤매너 반영 정도
   - 어미 패턴, 키워드 사용 적절성

2. **페르소나 적합성**
   - 고객 나이, 직업, 라이프스타일 맞춤 정도
   - 피부 고민 공감도

3. **자연스러움**
   - 문법적 정확성
   - 문장 흐름
   - 읽기 편한 정도

4. **구매 유도력**
   - 제품 구매 동기 부여
   - CTA (Call-to-Action) 효과성
   - 감성적 공감

### 톤 일관성 점수 (0-1)

| 점수 | 평가 |
|------|------|
| 0.7 이상 | 높은 일관성 |
| 0.4-0.7 | 보통 일관성 |
| 0.4 미만 | 낮은 일관성 |

## 결과 파일 구조

```
evaluation/
├── results/
│   └── test_results_20240115_143022.csv  # 전체 평가 결과
└── plots/
    ├── 01_brand_scores.png               # 브랜드별 점수
    ├── 02_purpose_scores.png             # 메시지 목적별 점수
    ├── 03_radar_chart.png                # 레이더 차트
    ├── 04_constraints_pie.png            # 제약 조건 통과율
    ├── 05_tone_consistency_heatmap.png   # 톤 일관성 히트맵
    ├── 06_generation_time.png            # 생성 시간 분포
    ├── 07_score_boxplot.png              # 점수 분포 박스플롯
    └── 08_comprehensive_dashboard.png    # 종합 대시보드
```

## CSV 주요 컬럼

### 기본 정보
- `persona_id`: 페르소나 ID
- `brand`: 브랜드명
- `message_purpose`: 메시지 목적

### 메시지
- `title`: 생성된 제목
- `body`: 생성된 본문
- `products`: 추천 제품 목록

### 평가 점수 (1-5점)
- `score_brand_tone`: 브랜드 톤 적합성
- `score_persona_fit`: 페르소나 적합성
- `score_naturalness`: 자연스러움
- `score_purchase_motivation`: 구매 유도력
- `score_overall`: 종합 점수 (평균)

### 제약 조건 (True/False)
- `constraint_title_valid`: 제목 40자 이내
- `constraint_body_valid`: 본문 350자 이내
- `constraint_forbidden_valid`: 금칙어 없음
- `constraints_all_met`: 전체 제약 조건 통과

### 톤 분석
- `tone_consistency`: 톤 일관성 점수 (0-1)
- `tone_endings_found`: 발견된 어미 패턴
- `tone_words_found`: 발견된 브랜드 키워드

### 시간 측정 (초)
- `generation_time_sec`: 메시지 생성 시간
- `evaluation_time_sec`: 평가 시간

## 시각화 차트 설명

### 1. 브랜드별 평균 점수 (01_brand_scores.png)
- 5개 브랜드의 4가지 평가 기준별 점수
- 브랜드 간 성능 비교

### 2. 메시지 목적별 평균 점수 (02_purpose_scores.png)
- 5가지 메시지 목적의 평가 점수
- 어떤 목적의 메시지가 더 좋은지 확인

### 3. 레이더 차트 (03_radar_chart.png)
- 브랜드별 4가지 기준 균형도
- 강점/약점 시각화

### 4. 제약 조건 통과율 (04_constraints_pie.png)
- 제목/본문 길이, 전체 제약 조건 통과율
- 파이 차트로 비율 표시

### 5. 톤 일관성 히트맵 (05_tone_consistency_heatmap.png)
- 브랜드 × 메시지 목적별 톤 일관성
- 어떤 조합이 톤을 잘 유지하는지 확인

### 6. 생성 시간 분포 (06_generation_time.png)
- 메시지 생성 소요 시간 히스토그램
- 브랜드별 평균 생성 시간

### 7. 점수 분포 박스플롯 (07_score_boxplot.png)
- 4가지 평가 기준 + 종합 점수 분포
- 중앙값, 사분위수, 이상치 확인

### 8. 종합 대시보드 (08_comprehensive_dashboard.png)
- 한 페이지에 모든 핵심 지표 요약
- 보고서 작성 시 활용

## 문제 해결

### 평가 점수가 전반적으로 낮은 경우

**브랜드 톤 점수가 낮다면:**
```python
# brands_db/brand_tone_corpus/*.csv 파일에 더 많은 톤 예시 추가
# src/prompts.py의 MESSAGE_GENERATOR_PROMPT 개선
```

**페르소나 적합성이 낮다면:**
```python
# src/graph_nodes.py의 persona_analyzer 노드 개선
# 리뷰 컨텍스트 활용 강화 (review_enricher)
```

**자연스러움이 낮다면:**
```python
# .env에서 TEMPERATURE 조정 (현재 0.7 → 0.5~0.8 실험)
# 메시지 생성 프롬프트 개선
```

**구매 유도력이 낮다면:**
```python
# 프롬프트에 CTA (Call-to-Action) 강조 추가
# 제품 혜택 강조 문구 개선
```

### 특정 브랜드만 점수가 낮은 경우

```python
# 해당 브랜드의 톤 코퍼스 데이터 보강
# brand_tone_corpus/[브랜드]_tone_texts.csv에 더 다양한 예시 추가
```

### 생성 시간이 너무 긴 경우

```python
# .env에서 MODEL_NAME을 gpt-3.5-turbo로 변경 (속도 우선)
# 벡터 검색 k 값 줄이기 (현재 5 → 3)
```

## 평가 기준 커스터마이징

### 평가 프롬프트 수정

`evaluation/evaluator.py`의 `_llm_evaluate()` 메서드에서 평가 기준 변경 가능:

```python
## 평가 기준 (각 1-5점)
1. **브랜드 톤 적합성**: ...
2. **페르소나 적합성**: ...
3. **자연스러움**: ...
4. **구매 유도력**: ...
5. **새로운 기준**: ...  # 추가 가능
```

### 브랜드 톤 특징 정의 수정

`evaluation/evaluator.py`의 `brand_tone_features` 딕셔너리 수정:

```python
self.brand_tone_features = {
    "etude": {
        "expected_endings": ["~해", "~야", "~지", "!"],
        "expected_words": ["너", "나", "우리", "완전"],
        "tone_desc": "발랄하고 트렌디한 톤"
    },
    # 브랜드별 커스터마이징...
}
```

## 다음 단계

평가 시스템 실행 후:

1. **CSV 분석**
   - Excel이나 Python pandas로 상세 분석
   - 점수가 낮은 메시지 찾아 패턴 파악

2. **시스템 개선**
   - 낮은 점수 영역 집중 개선
   - 프롬프트 튜닝, 데이터 보강

3. **재평가**
   - 개선 후 다시 전체 평가 실행
   - 개선 효과 측정

4. **A/B 테스트**
   - 동일 조건으로 여러 버전 생성
   - 버전 간 비교 분석

## 참고 자료

- 상세 평가 가이드: [evaluation/README.md](evaluation/README.md)
- 메인 시스템 문서: [README.md](README.md)
- 평가 코드: `evaluation/evaluator.py`
- 테스트 코드: `evaluation/test_all_combinations.py`
- 시각화 코드: `evaluation/visualize_results.py`
