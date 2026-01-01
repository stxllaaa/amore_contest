# 마케팅 메시지 생성 시스템 - 평가 모듈

## 개요

LLM 기반 자동 평가 및 시각화 시스템입니다.

## 주요 기능

### 1. 전체 조합 테스트 (test_all_combinations.py)
- 모든 페르소나 (8명) × 모든 메시지 목적 (5가지) = **40개 조합** 테스트
- 각 메시지에 대해 생성 시간 측정
- LLM 기반 4가지 품질 평가:
  - **브랜드 톤 적합성** (1-5점)
  - **페르소나 적합성** (1-5점)
  - **자연스러움** (1-5점)
  - **구매 유도력** (1-5점)
- 제약 조건 자동 검증 (제목 40자, 본문 350자, 금칙어)
- 브랜드 톤 특징 분석 (어미 패턴, 키워드)
- 결과를 CSV로 저장

### 2. 자동 품질 평가 (evaluator.py)
- LLM을 활용한 객관적 평가
- 브랜드별 기대 톤 특징 정의
- 형용사, 어미 패턴 자동 추출
- 톤 일관성 점수 계산

### 3. 시각화 대시보드 (visualize_results.py)
- **8가지 차트** 자동 생성:
  1. 브랜드별 평균 점수 막대 차트
  2. 메시지 목적별 평균 점수 막대 차트
  3. 평가 기준별 레이더 차트
  4. 제약 조건 통과율 파이 차트
  5. 브랜드별 톤 일관성 히트맵
  6. 생성 시간 분포 히스토그램
  7. 점수 분포 박스플롯
  8. 종합 대시보드 (한 페이지 요약)
- 고해상도 PNG 파일 저장 (300 DPI)

## 설치

```bash
# 기본 패키지 설치 (메인 requirements.txt)
pip install -r requirements.txt

# 평가 모듈 추가 패키지 설치
pip install -r evaluation/requirements.txt
```

## 사용 방법

### 1단계: 전체 조합 테스트 실행

```bash
python evaluation/test_all_combinations.py
```

**실행 시간:** 약 20-30분 (40개 메시지 × 평균 30초)

**출력:**
- `evaluation/results/test_results_YYYYMMDD_HHMMSS.csv` - 전체 테스트 결과
- 콘솔에 진행 상황 및 요약 통계 출력

**CSV 컬럼:**
- 기본 정보: persona_id, brand, message_purpose 등
- 메시지: title, body, products
- 평가 점수: score_brand_tone, score_persona_fit, score_naturalness, score_purchase_motivation, score_overall
- 제약 조건: constraint_title_valid, constraint_body_valid 등
- 톤 분석: tone_consistency, tone_endings_found 등
- 시간: generation_time_sec, evaluation_time_sec
- 피드백: feedback

### 2단계: 시각화 대시보드 생성

```bash
python evaluation/visualize_results.py
```

**출력:**
- `evaluation/plots/01_brand_scores.png`
- `evaluation/plots/02_purpose_scores.png`
- `evaluation/plots/03_radar_chart.png`
- `evaluation/plots/04_constraints_pie.png`
- `evaluation/plots/05_tone_consistency_heatmap.png`
- `evaluation/plots/06_generation_time.png`
- `evaluation/plots/07_score_boxplot.png`
- `evaluation/plots/08_comprehensive_dashboard.png`

## 평가 기준 상세

### 1. 브랜드 톤 적합성 (1-5점)

브랜드의 고유한 톤앤매너가 잘 반영되었는지 평가합니다.

| 브랜드 | 기대 톤 특징 | 예시 어미 | 예시 키워드 |
|--------|--------------|-----------|-------------|
| 에뛰드 | 발랄하고 트렌디한 톤, 반말 | ~해, ~야, ~지, ! | 너, 우리, 완전, 진짜 |
| 라네즈 | 친근하고 실용적인 톤 | ~해요, ~해줘요, ~해보세요 | 고민, 일상, 함께, 촉촉한 |
| 헤라 | 세련되고 프로페셔널한 톤 | ~니다, ~세요, ~습니다 | 세련된, 프로페셔널, 완벽한 |
| 설화수 | 고급스럽고 전통적인 톤 | ~니다, ~세요, ~습니다 | 전통, 명품, 귀한, 빛나는 |
| 아이오페 | 과학적이고 전문적인 톤 | ~니다, ~세요, ~습니다 | 과학적, 임상, 효과, 솔루션 |

### 2. 페르소나 적합성 (1-5점)

고객의 나이, 직업, 라이프스타일에 맞는 메시지인지 평가합니다.

- 나이대별 적절한 언어 사용
- 직업과 라이프스타일 반영
- 피부 고민에 대한 공감

### 3. 자연스러움 (1-5점)

문장이 자연스럽고 읽기 편한지 평가합니다.

- 문법적 정확성
- 문장 흐름
- 과도한 특수문자 사용 여부

### 4. 구매 유도력 (1-5점)

제품 구매 의욕을 자극하는지 평가합니다.

- 제품 혜택 강조
- 행동 유도 문구 (CTA)
- 감성적 공감

## 제약 조건 검증

- **제목 길이:** 40자 이내
- **본문 길이:** 350자 이내
- **금칙어:** 경쟁사 브랜드명 (LG생활건강, 코스맥스, 에스티로더 등)
- **특수문자:** 과도한 사용 금지 (5개 이내)

## 톤 일관성 분석

브랜드별로 기대되는 어미 패턴과 키워드가 실제로 사용되었는지 분석합니다.

**톤 일관성 점수 = (발견된 어미 / 기대 어미) × 0.5 + (발견된 키워드 / 기대 키워드) × 0.5**

- 0.7 이상: 높은 일관성
- 0.4-0.7: 보통 일관성
- 0.4 미만: 낮은 일관성

## 결과 해석 가이드

### 점수 해석

| 점수 | 평가 | 의미 |
|------|------|------|
| 4.5-5.0 | 우수 | 매우 높은 품질, 즉시 사용 가능 |
| 3.5-4.4 | 양호 | 높은 품질, 소폭 수정 후 사용 가능 |
| 2.5-3.4 | 보통 | 개선 필요 |
| 1.5-2.4 | 미흡 | 재생성 권장 |
| 1.0-1.4 | 불량 | 재생성 필수 |

### 개선 방향

**브랜드 톤 점수가 낮은 경우:**
- 브랜드 톤 코퍼스 데이터 보강
- 프롬프트의 톤 가이드라인 강화

**페르소나 적합성이 낮은 경우:**
- 페르소나 분석 노드 개선
- 리뷰 컨텍스트 활용 강화

**자연스러움이 낮은 경우:**
- 온도 파라미터 조정 (temperature)
- 메시지 생성 프롬프트 개선

**구매 유도력이 낮은 경우:**
- CTA(Call-to-Action) 문구 강화
- 제품 혜택 강조 프롬프트 추가

## 트러블슈팅

### 한글 폰트 깨짐 (시각화)

**Windows:**
```python
plt.rc('font', family='Malgun Gothic')
```

**Mac:**
```python
plt.rc('font', family='AppleGothic')
```

**Linux:**
```bash
sudo apt-get install fonts-noto-cjk
```

### 테스트 실행 시간이 너무 긴 경우

특정 페르소나만 테스트하려면 `test_all_combinations.py`를 수정:

```python
# 페르소나 일부만 테스트
self.personas = ["persona_001", "persona_002"]
```

### CSV 파일이 없다는 오류

먼저 `test_all_combinations.py`를 실행하여 결과 CSV를 생성해야 합니다.

## 추가 개발 아이디어

1. **A/B 테스트 자동화**
   - 동일 조건으로 여러 메시지 생성 후 비교

2. **실시간 모니터링 대시보드**
   - Streamlit으로 웹 대시보드 구현

3. **회귀 테스트**
   - 시스템 업데이트 후 성능 변화 추적

4. **사람 평가 vs LLM 평가 비교**
   - 실제 마케터의 평가와 LLM 평가 상관관계 분석

5. **다변량 분석**
   - 어떤 요소가 점수에 가장 큰 영향을 주는지 분석

## 라이센스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.
