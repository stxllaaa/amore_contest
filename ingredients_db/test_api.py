"""
공공데이터 API 테스트 스크립트
화장품 성분 정보 API가 정상적으로 작동하는지 확인
"""

import requests
import json

# API 설정
API_KEY = "17a1bf44d8263d736313b71b8922a479c9e5b8af16d11c699e64a3b2a1ce7798"
API_URL = "https://apis.data.go.kr/1471000/CsmtcsIngdCpntInfoService01/getCsmtcsIngdCpntInfoService01"


def test_api_connection():
    """API 연결 테스트"""
    print("="*60)
    print("공공데이터 API 연결 테스트")
    print("="*60)

    # 테스트할 성분 목록 (주요 화장품 성분)
    test_ingredients = [
        "Water",
        "Glycerin",
        "Niacinamide",
        "Hyaluronic Acid",
        "Retinol"
    ]

    results = []

    for idx, ingredient in enumerate(test_ingredients, 1):
        print(f"\n[{idx}/{len(test_ingredients)}] 테스트 성분: {ingredient}")

        try:
            # API 호출
            params = {
                'serviceKey': API_KEY,
                'ingdEng': ingredient,
                'type': 'json',
                'numOfRows': 1
            }

            response = requests.get(API_URL, params=params, timeout=10)

            print(f"   상태 코드: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # 응답 구조 출력
                print(f"   응답 구조: {list(data.keys())}")

                # body 확인
                if 'body' in data:
                    body = data['body']
                    print(f"   Body 키: {list(body.keys())}")

                    if 'items' in body:
                        items = body['items']
                        print(f"   Items 타입: {type(items)}")
                        print(f"   Items 개수: {len(items) if isinstance(items, list) else 'N/A'}")

                        if items and len(items) > 0:
                            item = items[0]
                            korean_name = item.get('ingdNameKor', 'N/A')
                            print(f"   ✓ 한글 성분명: {korean_name}")

                            results.append({
                                'eng': ingredient,
                                'kor': korean_name,
                                'status': 'success'
                            })
                        else:
                            print(f"   ✗ 결과 없음")
                            results.append({
                                'eng': ingredient,
                                'kor': None,
                                'status': 'no_result'
                            })
                    else:
                        print(f"   ✗ items 키가 없음")
                        results.append({
                            'eng': ingredient,
                            'kor': None,
                            'status': 'error'
                        })
                else:
                    print(f"   ✗ body 키가 없음")
                    print(f"   전체 응답: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                    results.append({
                        'eng': ingredient,
                        'kor': None,
                        'status': 'error'
                    })

            elif response.status_code == 403:
                print(f"   ✗ 권한 오류 (403): API 키가 잘못되었거나 권한이 없습니다")
                results.append({
                    'eng': ingredient,
                    'kor': None,
                    'status': 'forbidden'
                })
                break

            else:
                print(f"   ✗ 오류 응답: {response.text[:200]}")
                results.append({
                    'eng': ingredient,
                    'kor': None,
                    'status': f'error_{response.status_code}'
                })

        except requests.exceptions.Timeout:
            print(f"   ✗ 타임아웃")
            results.append({
                'eng': ingredient,
                'kor': None,
                'status': 'timeout'
            })

        except Exception as e:
            print(f"   ✗ 예외 발생: {e}")
            results.append({
                'eng': ingredient,
                'kor': None,
                'status': 'exception'
            })

    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)

    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)

    print(f"\n성공: {success_count}/{total_count}")

    if success_count > 0:
        print("\n✓ 성공한 매핑:")
        for r in results:
            if r['status'] == 'success':
                print(f"  - {r['eng']} → {r['kor']}")

    failed = [r for r in results if r['status'] != 'success']
    if failed:
        print(f"\n✗ 실패: {len(failed)}개")
        for r in failed:
            print(f"  - {r['eng']}: {r['status']}")

    # 결론
    print("\n" + "="*60)
    if success_count > 0:
        print("✓ API 연결 성공!")
        print(f"공공데이터 API를 사용할 수 있습니다.")
    elif any(r['status'] == 'forbidden' for r in results):
        print("✗ API 키 권한 오류")
        print("API 키를 확인하거나 공공데이터포털에서 활용신청을 확인하세요.")
    else:
        print("✗ API 연결 실패")
        print("네트워크 연결을 확인하거나 API 엔드포인트를 확인하세요.")
    print("="*60)

    return results


def test_single_ingredient(ingredient_name):
    """특정 성분 하나만 테스트"""
    print(f"\n단일 성분 테스트: {ingredient_name}")
    print("-" * 40)

    try:
        params = {
            'serviceKey': API_KEY,
            'ingdEng': ingredient_name,
            'type': 'json'
        }

        response = requests.get(API_URL, params=params, timeout=10)

        print(f"상태 코드: {response.status_code}")
        print(f"\n전체 응답:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    except Exception as e:
        print(f"오류: {e}")


if __name__ == "__main__":
    # 기본 테스트 실행
    results = test_api_connection()

    # 추가 테스트가 필요한 경우
    # test_single_ingredient("Glycerin")
