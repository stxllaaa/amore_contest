# Vercel 배포 가이드

## 배포 전 준비사항

### 1. 환경 변수 설정

Vercel 프로젝트 설정에서 다음 환경 변수를 추가해야 합니다:

- `GOOGLE_API_KEY`: Google Gemini API 키

### 2. Vercel CLI 설치 (선택사항)

```bash
npm install -g vercel
```

## 배포 방법

### 방법 1: Vercel CLI 사용

1. 프로젝트 디렉토리에서 다음 명령어 실행:

```bash
vercel
```

2. 프롬프트에 따라 설정 진행
3. 환경 변수 설정:

```bash
vercel env add GOOGLE_API_KEY
```

4. 배포:

```bash
vercel --prod
```

### 방법 2: GitHub 연동 (권장)

1. GitHub에 저장소 푸시
2. [Vercel 대시보드](https://vercel.com)에서 "New Project" 클릭
3. GitHub 저장소 선택
4. 환경 변수 설정:
   - `GOOGLE_API_KEY`: Google Gemini API 키
5. "Deploy" 클릭

## 배포 후 확인사항

1. 메인 페이지 접속 확인
2. 폼 작성 및 메시지 생성 테스트
3. API 응답 시간 확인 (첫 요청은 Cold Start로 인해 느릴 수 있음)

## 로컬 테스트

배포 전 로컬에서 테스트:

```bash
# 가상환경 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 문제 해결

### 1. 벡터 스토어 오류

벡터 스토어가 없으면 자동으로 생성됩니다. 최초 요청 시 시간이 오래 걸릴 수 있습니다.

### 2. API 타임아웃

Vercel Serverless Functions는 기본적으로 10초 타임아웃이 있습니다. Pro 플랜에서는 60초까지 가능합니다.

### 3. 메모리 부족

벡터 스토어가 큰 경우 메모리 부족이 발생할 수 있습니다. Vercel Pro 플랜에서 메모리를 늘릴 수 있습니다.

## 성능 최적화

1. 벡터 스토어를 미리 생성하여 포함
2. Cold Start 최소화를 위해 자주 사용하는 엔드포인트 핑
3. 캐싱 활용

## 비용 관리

- Vercel Hobby 플랜: 무료 (제한적)
- Vercel Pro 플랜: $20/월 (권장)
- Google Gemini API: 사용량에 따라 과금

## 보안

- `.env` 파일은 절대 커밋하지 마세요
- API 키는 환경 변수로만 관리
- CORS 설정 확인
