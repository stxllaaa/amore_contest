"""
평가 시스템 빠른 실행 스크립트
"""

import sys
import subprocess
from pathlib import Path


def run_command(command: str, description: str):
    """명령 실행 헬퍼"""
    print("\n" + "="*60)
    print(f"[실행] {description}")
    print("="*60)

    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print(f"\n[ERROR] {description} 실패")
        return False

    return True


def main():
    """메인 실행 함수"""

    print("\n" + "="*60)
    print("아모레퍼시픽 CRM 마케팅 메시지 생성 시스템")
    print("평가 및 시각화 자동 실행")
    print("="*60)

    print("\n다음 작업을 순서대로 실행합니다:")
    print("1. 전체 조합 테스트 (40개 메시지 생성 및 평가)")
    print("2. 시각화 대시보드 생성 (8가지 차트)")
    print("\n예상 소요 시간: 약 20-30분")

    response = input("\n계속 진행하시겠습니까? (y/N): ").strip().lower()

    if response != 'y':
        print("취소되었습니다.")
        return

    # 1. 전체 조합 테스트
    success = run_command(
        "python evaluation/test_all_combinations.py",
        "전체 조합 테스트"
    )

    if not success:
        print("\n테스트 실행 중 오류가 발생했습니다.")
        return

    # 2. 시각화
    success = run_command(
        "python evaluation/visualize_results.py",
        "시각화 대시보드 생성"
    )

    if not success:
        print("\n시각화 생성 중 오류가 발생했습니다.")
        return

    # 완료
    print("\n" + "="*60)
    print("모든 작업이 완료되었습니다!")
    print("="*60)

    print("\n[결과 파일]")
    print("  CSV: evaluation/results/")
    print("  차트: evaluation/plots/")

    # 결과 디렉토리 열기 (Windows)
    try:
        import platform
        if platform.system() == 'Windows':
            response = input("\n결과 폴더를 여시겠습니까? (y/N): ").strip().lower()
            if response == 'y':
                subprocess.run("explorer evaluation\\plots", shell=True)
    except:
        pass


if __name__ == "__main__":
    main()
