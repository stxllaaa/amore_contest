"""
화장품 성분 DB 구축 (최적화 버전)
- HuggingFace 데이터 사용
- Google Gemini로 성분명 번역
- 벡터 스토어 생성
"""

import pandas as pd
from datasets import load_dataset
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json

load_dotenv()


def download_huggingface_data():
    """HuggingFace에서 화장품 성분 데이터 다운로드"""
    print("\n[1/4] HuggingFace 데이터 다운로드 중...")

    try:
        dataset = load_dataset("yavuzyilmaz/cosmetic-ingredients")
        df = pd.DataFrame(dataset['train'])

        print(f"   ✓ {len(df)}개 성분 데이터 다운로드 완료")
        print(f"   컬럼: {df.columns.tolist()}")

        return df

    except Exception as e:
        print(f"   ✗ 오류: {e}")
        print("   ℹ 대체 방법: 수동으로 샘플 데이터 생성")
        return create_sample_ingredients()


def create_sample_ingredients():
    """샘플 성분 데이터 생성 (HuggingFace 접속 실패 시)"""
    print("   샘플 데이터 생성 중...")

    sample_data = [
        {
            'ingredient': 'Hyaluronic Acid',
            'function': 'Hydration, plumping, anti-aging',
            'description': 'A powerful humectant that can hold up to 1000 times its weight in water'
        },
        {
            'ingredient': 'Niacinamide',
            'function': 'Brightening, pore minimizing, oil control',
            'description': 'Also known as Vitamin B3, helps improve skin texture and reduce hyperpigmentation'
        },
        {
            'ingredient': 'Retinol',
            'function': 'Anti-aging, cell turnover, collagen production',
            'description': 'Vitamin A derivative that promotes skin renewal and reduces wrinkles'
        },
        {
            'ingredient': 'Vitamin C',
            'function': 'Brightening, antioxidant, collagen synthesis',
            'description': 'Powerful antioxidant that brightens skin and protects against environmental damage'
        },
        {
            'ingredient': 'Ceramides',
            'function': 'Barrier repair, moisture retention',
            'description': 'Lipids that help restore and maintain the skin barrier'
        },
        {
            'ingredient': 'Peptides',
            'function': 'Anti-aging, firmness, collagen production',
            'description': 'Amino acid chains that signal skin to produce more collagen'
        },
        {
            'ingredient': 'AHA/BHA',
            'function': 'Exfoliation, cell turnover, pore clearing',
            'description': 'Chemical exfoliants that remove dead skin cells and unclog pores'
        },
        {
            'ingredient': 'Centella Asiatica',
            'function': 'Soothing, healing, anti-inflammatory',
            'description': 'Also known as Cica or Tiger Grass, calms irritated skin'
        },
        {
            'ingredient': 'Green Tea Extract',
            'function': 'Antioxidant, anti-inflammatory, soothing',
            'description': 'Rich in polyphenols that protect skin from damage'
        },
        {
            'ingredient': 'Snail Mucin',
            'function': 'Hydration, repair, anti-aging',
            'description': 'Contains glycoproteins and hyaluronic acid for skin regeneration'
        }
    ]

    return pd.DataFrame(sample_data)


def translate_with_gemini(ingredients_df):
    """Google Gemini로 성분명 한글 번역"""
    print("\n[2/4] Google Gemini로 성분명 번역 중...")

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash-exp",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 성분명 추출
    name_col = None
    for col in ['ingredient', 'name', 'ingredient_name']:
        if col in ingredients_df.columns:
            name_col = col
            break

    if not name_col:
        print("   ✗ 성분명 컬럼을 찾을 수 없습니다")
        return ingredients_df

    # 배치로 번역 (10개씩)
    batch_size = 10
    total = len(ingredients_df)
    translated_names = []

    for i in range(0, total, batch_size):
        batch = ingredients_df[name_col].iloc[i:i+batch_size].tolist()

        prompt = f"""다음 화장품 성분의 영문명을 한글로 번역해주세요.
일반적으로 사용되는 화장품 용어로 번역하되, 전문 용어는 한글 음차를 사용하세요.

JSON 형식으로 응답해주세요:
{{
  "translations": [
    {{"eng": "영문명", "kor": "한글명"}},
    ...
  ]
}}

영문 성분명 목록:
{batch}
"""

        try:
            response = llm.invoke(prompt)
            content = response.content.strip()

            # Markdown 코드 블록 제거
            if content.startswith("```"):
                lines = content.split('\n')
                content = '\n'.join(lines[1:-1])

            result = json.loads(content)
            translations = result.get('translations', [])

            for trans in translations:
                translated_names.append({
                    'eng': trans['eng'],
                    'kor': trans['kor']
                })

            print(f"   [{i+1}-{min(i+batch_size, total)}/{total}] 번역 완료")

        except Exception as e:
            print(f"   ✗ 배치 {i//batch_size + 1} 오류: {e}")
            # 실패한 배치는 영문 그대로 사용
            for eng in batch:
                translated_names.append({'eng': eng, 'kor': eng})

    # DataFrame에 한글명 추가
    translation_df = pd.DataFrame(translated_names)
    ingredients_df = ingredients_df.merge(
        translation_df,
        left_on=name_col,
        right_on='eng',
        how='left'
    )

    # 매칭되지 않은 것은 영문 그대로
    ingredients_df['ingredient_kor'] = ingredients_df['kor'].fillna(
        ingredients_df[name_col]
    )

    print(f"   ✓ {len(translated_names)}개 성분명 번역 완료")

    return ingredients_df


def create_ingredient_csv(ingredients_df):
    """성분 DB CSV 파일 생성"""
    print("\n[3/4] 성분 DB CSV 생성 중...")

    # 컬럼 정리
    name_col = None
    for col in ['ingredient', 'name', 'ingredient_name']:
        if col in ingredients_df.columns:
            name_col = col
            break

    function_col = None
    for col in ['function', 'effect', 'benefits']:
        if col in ingredients_df.columns:
            function_col = col
            break

    desc_col = None
    for col in ['description', 'desc', 'detail']:
        if col in ingredients_df.columns:
            desc_col = col
            break

    # 최종 데이터 구조
    final_data = []

    for _, row in ingredients_df.iterrows():
        final_data.append({
            'ingredient_id': f"ingr_{len(final_data)+1:04d}",
            'ingredient_eng': row[name_col] if name_col else '',
            'ingredient_kor': row.get('ingredient_kor', row[name_col] if name_col else ''),
            'function': row[function_col] if function_col else '',
            'description': row[desc_col] if desc_col else '',
            'skin_concerns': extract_skin_concerns(
                row[function_col] if function_col else ''
            )
        })

    result_df = pd.DataFrame(final_data)

    # 저장
    output_path = Path(__file__).parent / "cosmetic_ingredients.csv"
    result_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"   ✓ {len(result_df)}개 성분 데이터 저장")
    print(f"   파일: {output_path}")

    return result_df


def extract_skin_concerns(function_text):
    """효능에서 피부 고민 추출"""
    if not function_text:
        return ""

    concerns_mapping = {
        'hydration': '건조',
        'moisture': '건조',
        'dry': '건조',
        'brightening': '칙칙함',
        'whitening': '칙칙함',
        'anti-aging': '주름',
        'wrinkle': '주름',
        'aging': '주름',
        'pore': '모공',
        'acne': '피지',
        'oil': '피지',
        'sensitive': '민감함',
        'soothing': '민감함',
        'firming': '탄력저하',
        'elasticity': '탄력저하'
    }

    detected_concerns = []
    function_lower = function_text.lower()

    for keyword, concern in concerns_mapping.items():
        if keyword in function_lower and concern not in detected_concerns:
            detected_concerns.append(concern)

    return ', '.join(detected_concerns)


def main():
    """메인 실행"""
    print("="*60)
    print("화장품 성분 DB 구축 (최적화 버전)")
    print("="*60)

    # 1. HuggingFace 데이터 다운로드
    df = download_huggingface_data()

    # 2. 한글 번역
    df = translate_with_gemini(df)

    # 3. CSV 생성
    result_df = create_ingredient_csv(df)

    # 4. 완료
    print("\n" + "="*60)
    print("✓ 성분 DB 구축 완료!")
    print("="*60)
    print(f"\n샘플 데이터:\n{result_df.head()}")


if __name__ == "__main__":
    main()
