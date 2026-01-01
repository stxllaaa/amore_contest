"""
마케팅 메시지 품질 평가 모듈
LLM을 활용한 자동 평가 및 톤 분석
"""

import os
import re
import json
from typing import Dict, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

# 환경변수 로드
load_dotenv()


class MessageEvaluator:
    """메시지 품질 자동 평가 클래스"""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("MODEL_NAME", "models/gemini-2.5-flash"),
            temperature=0.3,  # 평가는 일관성을 위해 낮은 temperature
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # 브랜드별 기대 톤 특징
        self.brand_tone_features = {
            "etude": {
                "expected_endings": ["~해", "~야", "~지", "!"],
                "expected_words": ["너", "나", "우리", "요즘", "완전", "진짜"],
                "tone_desc": "발랄하고 트렌디한 톤, 반말, 의성어/의태어 빈번"
            },
            "laneige": {
                "expected_endings": ["~해요", "~해줘요", "~해보세요"],
                "expected_words": ["고민", "일상", "함께", "건강한", "촉촉한"],
                "tone_desc": "친근하고 실용적인 톤, ~해요 말투, 공감형"
            },
            "hera": {
                "expected_endings": ["~니다", "~세요", "~습니다"],
                "expected_words": ["세련된", "프로페셔널", "완벽한", "엘레강스"],
                "tone_desc": "세련되고 프로페셔널한 톤, 격식체, 우아함"
            },
            "sulwhasoo": {
                "expected_endings": ["~니다", "~세요", "~습니다"],
                "expected_words": ["전통", "명품", "귀한", "빛나는", "아름다운"],
                "tone_desc": "고급스럽고 전통적인 톤, 한자어 사용, 격식 높음"
            },
            "iope": {
                "expected_endings": ["~니다", "~세요", "~습니다"],
                "expected_words": ["과학적", "임상", "효과", "케어", "솔루션"],
                "tone_desc": "과학적이고 전문적인 톤, 근거 기반, 신뢰감"
            }
        }

    def evaluate_message(
        self,
        title: str,
        body: str,
        brand: str,
        persona_info: Dict,
        message_purpose: str
    ) -> Dict:
        """
        메시지 종합 평가

        Returns:
            {
                'scores': {
                    'brand_tone': 1-5,
                    'persona_fit': 1-5,
                    'naturalness': 1-5,
                    'purchase_motivation': 1-5,
                    'overall': 평균 점수
                },
                'tone_analysis': {...},
                'constraints_check': {...},
                'feedback': str
            }
        """
        # 1. LLM 기반 품질 평가
        scores = self._llm_evaluate(title, body, brand, persona_info, message_purpose)

        # 2. 톤 특징 분석
        tone_analysis = self._analyze_tone(title + " " + body, brand)

        # 3. 제약 조건 검증
        constraints = self._check_constraints(title, body)

        # 4. 종합 점수 계산
        overall_score = sum(scores.values()) / len(scores)

        return {
            'scores': {
                **scores,
                'overall': round(overall_score, 2)
            },
            'tone_analysis': tone_analysis,
            'constraints_check': constraints,
            'feedback': self._generate_feedback(scores, tone_analysis, constraints)
        }

    def _llm_evaluate(
        self,
        title: str,
        body: str,
        brand: str,
        persona_info: Dict,
        message_purpose: str
    ) -> Dict[str, float]:
        """LLM을 활용한 4가지 항목 평가"""

        # 브랜드 한글명 매핑
        brand_names = {
            "etude": "에뛰드",
            "laneige": "라네즈",
            "hera": "헤라",
            "sulwhasoo": "설화수",
            "iope": "아이오페"
        }

        brand_name = brand_names.get(brand, brand)
        tone_desc = self.brand_tone_features.get(brand, {}).get("tone_desc", "")

        prompt = f"""다음 마케팅 메시지를 4가지 기준으로 평가하고 각각 1-5점을 부여하세요.

## 메시지
제목: {title}
본문: {body}

## 브랜드 정보
브랜드: {brand_name}
기대 톤: {tone_desc}

## 고객 정보
- 나이: {persona_info.get('age', 'N/A')}세
- 성별: {persona_info.get('gender', 'N/A')}
- 직업: {persona_info.get('occupation', 'N/A')}
- 피부고민: {persona_info.get('skin_concerns', 'N/A')}
- 라이프스타일: {persona_info.get('lifestyle_keywords', 'N/A')}

## 메시지 목적
{message_purpose}

## 평가 기준 (각 1-5점)
1. **브랜드 톤 적합성**: 브랜드의 톤앤매너가 잘 반영되었는가?
2. **페르소나 적합성**: 고객의 나이, 직업, 라이프스타일에 맞는 메시지인가?
3. **자연스러움**: 문장이 자연스럽고 읽기 편한가?
4. **구매 유도력**: 제품 구매 의욕을 자극하는가?

JSON 형식으로만 응답하세요:
{{
  "brand_tone": 1-5,
  "persona_fit": 1-5,
  "naturalness": 1-5,
  "purchase_motivation": 1-5,
  "reasoning": "간단한 평가 이유"
}}
"""

        try:
            messages = [
                SystemMessage(content="당신은 마케팅 메시지 평가 전문가입니다."),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)

            # JSON 파싱
            result = json.loads(response.content)

            return {
                'brand_tone': float(result.get('brand_tone', 3)),
                'persona_fit': float(result.get('persona_fit', 3)),
                'naturalness': float(result.get('naturalness', 3)),
                'purchase_motivation': float(result.get('purchase_motivation', 3))
            }

        except Exception as e:
            print(f"[WARNING] LLM 평가 실패: {e}")
            # 기본값 반환
            return {
                'brand_tone': 3.0,
                'persona_fit': 3.0,
                'naturalness': 3.0,
                'purchase_motivation': 3.0
            }

    def _analyze_tone(self, text: str, brand: str) -> Dict:
        """브랜드별 톤 특징 분석"""

        features = self.brand_tone_features.get(brand, {})
        expected_endings = features.get("expected_endings", [])
        expected_words = features.get("expected_words", [])

        # 어미 패턴 분석
        ending_matches = []
        for ending in expected_endings:
            if ending in text:
                ending_matches.append(ending)

        # 키워드 분석
        word_matches = []
        for word in expected_words:
            if word in text:
                word_matches.append(word)

        # 문장 종결 어미 추출
        sentences = re.split(r'[.!?]', text)
        actual_endings = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 0:
                # 마지막 2-3글자 추출
                actual_endings.append(sent[-2:] if len(sent) >= 2 else sent)

        # 형용사 추출 (간단 버전 - 특정 패턴)
        adjectives = re.findall(r'(\w+한|\w+로운|\w+스러운|\w+적인)', text)

        # 톤 일관성 점수
        tone_consistency = (
            (len(ending_matches) / max(len(expected_endings), 1)) * 0.5 +
            (len(word_matches) / max(len(expected_words), 1)) * 0.5
        )

        return {
            'expected_endings_found': ending_matches,
            'expected_words_found': word_matches,
            'actual_endings': list(set(actual_endings[:5])),  # 상위 5개
            'adjectives_used': list(set(adjectives[:5])),
            'tone_consistency_score': round(min(tone_consistency, 1.0), 2),
            'total_sentences': len([s for s in sentences if s.strip()])
        }

    def _check_constraints(self, title: str, body: str) -> Dict:
        """제약 조건 검증"""

        title_len = len(title)
        body_len = len(body)

        # 금칙어 체크
        forbidden_words = ['LG생활건강', '코스맥스', '에스티로더', '로레알', '시세이도']
        found_forbidden = [word for word in forbidden_words if word in title or word in body]

        # 특수문자 과다 사용 체크
        special_chars = re.findall(r'[!?~♥♡★☆]', title + body)

        return {
            'title_length': title_len,
            'title_valid': title_len <= 40,
            'body_length': body_len,
            'body_valid': body_len <= 350,
            'forbidden_words_found': found_forbidden,
            'forbidden_words_valid': len(found_forbidden) == 0,
            'special_char_count': len(special_chars),
            'special_char_valid': len(special_chars) <= 5,
            'all_constraints_met': (
                title_len <= 40 and
                body_len <= 350 and
                len(found_forbidden) == 0
            )
        }

    def _generate_feedback(
        self,
        scores: Dict,
        tone_analysis: Dict,
        constraints: Dict
    ) -> str:
        """피드백 생성"""

        feedback = []

        # 점수 기반 피드백
        if scores['brand_tone'] < 3:
            feedback.append("브랜드 톤앤매너 개선 필요")
        if scores['persona_fit'] < 3:
            feedback.append("페르소나 타겟팅 약함")
        if scores['naturalness'] < 3:
            feedback.append("문장 자연스러움 부족")
        if scores['purchase_motivation'] < 3:
            feedback.append("구매 유도력 강화 필요")

        # 톤 일관성 피드백
        if tone_analysis['tone_consistency_score'] < 0.3:
            feedback.append(f"브랜드 톤 특징 반영 부족 (일관성: {tone_analysis['tone_consistency_score']:.1%})")

        # 제약 조건 피드백
        if not constraints['title_valid']:
            feedback.append(f"제목 길이 초과 ({constraints['title_length']}자 > 40자)")
        if not constraints['body_valid']:
            feedback.append(f"본문 길이 초과 ({constraints['body_length']}자 > 350자)")
        if not constraints['forbidden_words_valid']:
            feedback.append(f"금칙어 포함: {', '.join(constraints['forbidden_words_found'])}")

        # 긍정 피드백
        if not feedback:
            feedback.append("모든 기준을 만족하는 우수한 메시지입니다")

        return " | ".join(feedback)


def quick_evaluate(title: str, body: str, brand: str) -> Dict:
    """빠른 평가 함수"""
    evaluator = MessageEvaluator()
    return evaluator.evaluate_message(
        title=title,
        body=body,
        brand=brand,
        persona_info={},
        message_purpose="personalized"
    )
