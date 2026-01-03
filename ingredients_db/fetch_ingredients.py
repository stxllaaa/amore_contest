"""
화장품 성분 데이터 수집 스크립트
1. HuggingFace에서 영문 성분 데이터 다운로드
2. 공공데이터 API에서 한글 성분명 가져오기
3. 매핑 테이블 생성
"""

import requests
import pandas as pd
from datasets import load_dataset
import time
from pathlib import Path

# 공공데이터 API 설정
API_KEY = "17a1bf44d8263d736313b71b8922a479c9e5b8af16d11c699e64a3b2a1ce7798"
API_URL = "https://apis.data.go.kr/1471000/CsmtcsIngdCpntInfoService01/getCsmtcsIngdCpntInfoService01"


def fetch_huggingface_data():
    """HuggingFace에서 화장품 성분 데이터 다운로드"""
    print("\n[1/3] HuggingFace 데이터 다운로드 중...")

    try:
        # 데이터셋 로드
        dataset = load_dataset("yavuzyilmaz/cosmetic-ingredients")

        # DataFrame으로 변환
        df = pd.DataFrame(dataset['train'])

        print(f"   ✓ {len(df)}개 성분 데이터 다운로드 완료")
        print(f"   컬럼: {df.columns.tolist()}")

        return df

    except Exception as e:
        print(f"   ✗ 오류 발생: {e}")
        return None


def fetch_korean_ingredients(ingredient_names):
    """공공데이터 API에서 한글 성분명 가져오기"""
    print("\n[2/3] 공공데이터 API에서 한글 성분명 가져오는 중...")

    korean_mapping = {}

    for idx, eng_name in enumerate(ingredient_names[:100]):  # 테스트용 100개만
        try:
            params = {
                'serviceKey': API_KEY,
                'ingdEng': eng_name,  # 영문 성분명
                'type': 'json'
            }

            response = requests.get(API_URL, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 응답에서 한글명 추출
                if 'body' in data and 'items' in data['body']:
                    items = data['body']['items']
                    if items and len(items) > 0:
                        korean_name = items[0].get('ingdNameKor', '')
                        if korean_name:
                            korean_mapping[eng_name] = korean_name
                            print(f"   [{idx+1}/{len(ingredient_names)}] {eng_name} → {korean_name}")

            # API 호출 제한 방지
            time.sleep(0.1)

        except Exception as e:
            print(f"   ✗ {eng_name}: {e}")
            continue

    print(f"\n   ✓ {len(korean_mapping)}개 한글 매핑 완료")
    return korean_mapping


def create_ingredient_database(hf_data, korean_mapping):
    """성분 데이터베이스 생성"""
    print("\n[3/3] 통합 데이터베이스 생성 중...")

    # 영문 성분명 컬럼 찾기
    name_col = None
    for col in ['ingredient', 'name', 'ingredient_name']:
        if col in hf_data.columns:
            name_col = col
            break

    if not name_col:
        print("   ✗ 성분명 컬럼을 찾을 수 없습니다")
        return None

    # 효능 컬럼 찾기
    effect_col = None
    for col in ['effect', 'function', 'description', 'benefits']:
        if col in hf_data.columns:
            effect_col = col
            break

    # 데이터 통합
    integrated_data = []

    for _, row in hf_data.iterrows():
        eng_name = row[name_col]
        korean_name = korean_mapping.get(eng_name, eng_name)  # 매핑 없으면 영문 그대로
        effect = row[effect_col] if effect_col else ""

        integrated_data.append({
            'ingredient_eng': eng_name,
            'ingredient_kor': korean_name,
            'effect': effect,
            'category': row.get('category', ''),
            'safety': row.get('safety', '')
        })

    df = pd.DataFrame(integrated_data)

    # CSV로 저장
    output_path = Path(__file__).parent / "cosmetic_ingredients.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"   ✓ {len(df)}개 성분 데이터 저장 완료")
    print(f"   파일: {output_path}")

    return df


def main():
    """메인 실행 함수"""
    print("="*60)
    print("화장품 성분 데이터 수집 시작")
    print("="*60)

    # 1. HuggingFace 데이터 다운로드
    hf_data = fetch_huggingface_data()
    if hf_data is None:
        return

    # 2. 한글 성분명 매핑
    # 영문 성분명 추출
    name_col = None
    for col in ['ingredient', 'name', 'ingredient_name']:
        if col in hf_data.columns:
            name_col = col
            break

    if name_col:
        ingredient_names = hf_data[name_col].unique().tolist()
        korean_mapping = fetch_korean_ingredients(ingredient_names)
    else:
        print("성분명 컬럼을 찾을 수 없어 한글 매핑을 건너뜁니다.")
        korean_mapping = {}

    # 3. 통합 데이터베이스 생성
    result_df = create_ingredient_database(hf_data, korean_mapping)

    if result_df is not None:
        print("\n" + "="*60)
        print("✓ 데이터 수집 완료!")
        print("="*60)
        print(f"\n데이터 샘플:\n{result_df.head()}")


if __name__ == "__main__":
    main()
