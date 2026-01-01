"""
테스트 결과 시각화 대시보드
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from matplotlib import font_manager
import platform

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ResultVisualizer:
    """테스트 결과 시각화 클래스"""

    def __init__(self, csv_path: str = None):
        """
        Args:
            csv_path: CSV 파일 경로 (None이면 가장 최근 파일 사용)
        """
        self.results_dir = Path("evaluation/results")

        # CSV 로드
        if csv_path is None:
            csv_path = self._get_latest_csv()

        self.df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"[로드] {csv_path}")
        print(f"[데이터] {len(self.df)}개 레코드")

        # 한글 폰트 설정
        self._setup_korean_font()

        # 스타일 설정
        sns.set_style("whitegrid")
        sns.set_palette("husl")

        # 그래프 저장 디렉토리
        self.plots_dir = Path("evaluation/plots")
        self.plots_dir.mkdir(exist_ok=True, parents=True)

    def _get_latest_csv(self) -> Path:
        """가장 최근 CSV 파일 가져오기"""
        csv_files = list(self.results_dir.glob("test_results_*.csv"))
        if not csv_files:
            raise FileNotFoundError("테스트 결과 파일이 없습니다. test_all_combinations.py를 먼저 실행하세요.")

        latest = max(csv_files, key=lambda p: p.stat().st_mtime)
        return latest

    def _setup_korean_font(self):
        """한글 폰트 설정"""
        # Windows의 경우 맑은 고딕 사용
        if platform.system() == 'Windows':
            plt.rc('font', family='Malgun Gothic')
        # Mac의 경우 AppleGothic
        elif platform.system() == 'Darwin':
            plt.rc('font', family='AppleGothic')
        # Linux의 경우 Noto Sans CJK
        else:
            try:
                plt.rc('font', family='Noto Sans CJK KR')
            except:
                print("[WARNING] 한글 폰트를 찾을 수 없습니다. 한글이 깨질 수 있습니다.")

        # 마이너스 기호 깨짐 방지
        plt.rc('axes', unicode_minus=False)

    def create_dashboard(self):
        """전체 대시보드 생성"""

        print("\n" + "="*60)
        print("시각화 대시보드 생성 중...")
        print("="*60)

        # 1. 브랜드별 점수
        self.plot_brand_scores()

        # 2. 메시지 목적별 점수
        self.plot_purpose_scores()

        # 3. 평가 기준별 레이더 차트
        self.plot_radar_chart()

        # 4. 제약 조건 통과율
        self.plot_constraints_pie()

        # 5. 브랜드별 톤 일관성
        self.plot_tone_consistency()

        # 6. 생성 시간 분포
        self.plot_generation_time()

        # 7. 점수 분포 박스플롯
        self.plot_score_distribution()

        # 8. 종합 대시보드
        self.plot_comprehensive_dashboard()

        print("\n" + "="*60)
        print("시각화 완료!")
        print(f"저장 위치: {self.plots_dir.absolute()}")
        print("="*60)

    def plot_brand_scores(self):
        """브랜드별 평균 점수"""
        plt.figure(figsize=(12, 6))

        # 브랜드별 4가지 점수
        brand_scores = self.df.groupby('brand')[[
            'score_brand_tone',
            'score_persona_fit',
            'score_naturalness',
            'score_purchase_motivation'
        ]].mean()

        brand_scores.plot(kind='bar', ax=plt.gca())
        plt.title('브랜드별 평균 평가 점수', fontsize=16, fontweight='bold')
        plt.xlabel('브랜드', fontsize=12)
        plt.ylabel('점수 (1-5)', fontsize=12)
        plt.legend(['브랜드 톤', '페르소나 적합', '자연스러움', '구매 유도력'], loc='best')
        plt.ylim(0, 5.5)
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(self.plots_dir / '01_brand_scores.png', dpi=300)
        plt.close()
        print("  [1/8] 브랜드별 점수 저장")

    def plot_purpose_scores(self):
        """메시지 목적별 평균 점수"""
        plt.figure(figsize=(12, 6))

        purpose_scores = self.df.groupby('message_purpose')[[
            'score_brand_tone',
            'score_persona_fit',
            'score_naturalness',
            'score_purchase_motivation'
        ]].mean()

        purpose_scores.plot(kind='bar', ax=plt.gca())
        plt.title('메시지 목적별 평균 평가 점수', fontsize=16, fontweight='bold')
        plt.xlabel('메시지 목적', fontsize=12)
        plt.ylabel('점수 (1-5)', fontsize=12)
        plt.legend(['브랜드 톤', '페르소나 적합', '자연스러움', '구매 유도력'], loc='best')
        plt.ylim(0, 5.5)
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(self.plots_dir / '02_purpose_scores.png', dpi=300)
        plt.close()
        print("  [2/8] 메시지 목적별 점수 저장")

    def plot_radar_chart(self):
        """평가 기준별 레이더 차트 (브랜드별)"""
        categories = ['브랜드 톤', '페르소나 적합', '자연스러움', '구매 유도력']
        score_cols = ['score_brand_tone', 'score_persona_fit', 'score_naturalness', 'score_purchase_motivation']

        brands = self.df['brand'].unique()
        num_brands = len(brands)

        fig, axes = plt.subplots(1, min(num_brands, 5), figsize=(15, 3), subplot_kw=dict(projection='polar'))
        if num_brands == 1:
            axes = [axes]

        for idx, brand in enumerate(brands[:5]):  # 최대 5개 브랜드만
            brand_data = self.df[self.df['brand'] == brand][score_cols].mean().values

            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            brand_data = brand_data.tolist()

            # 원을 완성하기 위해 첫 값을 마지막에 추가
            angles += angles[:1]
            brand_data += brand_data[:1]

            ax = axes[idx] if num_brands > 1 else axes[0]
            ax.plot(angles, brand_data, 'o-', linewidth=2, label=brand)
            ax.fill(angles, brand_data, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=8)
            ax.set_ylim(0, 5)
            ax.set_title(brand, fontsize=12, fontweight='bold')
            ax.grid(True)

        plt.tight_layout()
        plt.savefig(self.plots_dir / '03_radar_chart.png', dpi=300)
        plt.close()
        print("  [3/8] 레이더 차트 저장")

    def plot_constraints_pie(self):
        """제약 조건 통과율 파이 차트"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # 제목 길이
        title_valid = self.df['constraint_title_valid'].value_counts()
        axes[0].pie(title_valid, labels=['통과', '실패'], autopct='%1.1f%%', startangle=90)
        axes[0].set_title('제목 길이 제약 (≤40자)', fontsize=12, fontweight='bold')

        # 본문 길이
        body_valid = self.df['constraint_body_valid'].value_counts()
        axes[1].pie(body_valid, labels=['통과', '실패'], autopct='%1.1f%%', startangle=90)
        axes[1].set_title('본문 길이 제약 (≤350자)', fontsize=12, fontweight='bold')

        # 전체 제약
        all_valid = self.df['constraints_all_met'].value_counts()
        axes[2].pie(all_valid, labels=['통과', '실패'], autopct='%1.1f%%', startangle=90)
        axes[2].set_title('전체 제약 조건', fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.plots_dir / '04_constraints_pie.png', dpi=300)
        plt.close()
        print("  [4/8] 제약 조건 파이 차트 저장")

    def plot_tone_consistency(self):
        """브랜드별 톤 일관성 히트맵"""
        plt.figure(figsize=(10, 6))

        # 브랜드 × 메시지 목적별 톤 일관성
        tone_pivot = self.df.pivot_table(
            values='tone_consistency',
            index='brand',
            columns='message_purpose',
            aggfunc='mean'
        )

        sns.heatmap(tone_pivot, annot=True, fmt='.2f', cmap='YlGnBu', vmin=0, vmax=1)
        plt.title('브랜드별 톤 일관성 점수 (0-1)', fontsize=16, fontweight='bold')
        plt.xlabel('메시지 목적', fontsize=12)
        plt.ylabel('브랜드', fontsize=12)
        plt.tight_layout()

        plt.savefig(self.plots_dir / '05_tone_consistency_heatmap.png', dpi=300)
        plt.close()
        print("  [5/8] 톤 일관성 히트맵 저장")

    def plot_generation_time(self):
        """생성 시간 분포"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 히스토그램
        axes[0].hist(self.df['generation_time_sec'], bins=20, edgecolor='black', alpha=0.7)
        axes[0].axvline(self.df['generation_time_sec'].mean(), color='red', linestyle='--', label=f"평균: {self.df['generation_time_sec'].mean():.2f}초")
        axes[0].set_xlabel('생성 시간 (초)', fontsize=12)
        axes[0].set_ylabel('빈도', fontsize=12)
        axes[0].set_title('메시지 생성 시간 분포', fontsize=14, fontweight='bold')
        axes[0].legend()
        axes[0].grid(alpha=0.3)

        # 브랜드별 평균 생성 시간
        brand_time = self.df.groupby('brand')['generation_time_sec'].mean().sort_values()
        brand_time.plot(kind='barh', ax=axes[1], color='skyblue', edgecolor='black')
        axes[1].set_xlabel('평균 생성 시간 (초)', fontsize=12)
        axes[1].set_ylabel('브랜드', fontsize=12)
        axes[1].set_title('브랜드별 평균 생성 시간', fontsize=14, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.plots_dir / '06_generation_time.png', dpi=300)
        plt.close()
        print("  [6/8] 생성 시간 분포 저장")

    def plot_score_distribution(self):
        """점수 분포 박스플롯"""
        plt.figure(figsize=(12, 6))

        score_data = self.df[[
            'score_brand_tone',
            'score_persona_fit',
            'score_naturalness',
            'score_purchase_motivation',
            'score_overall'
        ]]

        score_data.columns = ['브랜드 톤', '페르소나 적합', '자연스러움', '구매 유도력', '종합']

        sns.boxplot(data=score_data)
        plt.title('평가 점수 분포 (박스플롯)', fontsize=16, fontweight='bold')
        plt.ylabel('점수 (1-5)', fontsize=12)
        plt.ylim(0, 5.5)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        plt.savefig(self.plots_dir / '07_score_boxplot.png', dpi=300)
        plt.close()
        print("  [7/8] 점수 분포 박스플롯 저장")

    def plot_comprehensive_dashboard(self):
        """종합 대시보드 (한 페이지에 모든 정보)"""
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. 브랜드별 종합 점수
        ax1 = fig.add_subplot(gs[0, :2])
        brand_overall = self.df.groupby('brand')['score_overall'].mean().sort_values(ascending=False)
        brand_overall.plot(kind='bar', ax=ax1, color='steelblue', edgecolor='black')
        ax1.set_title('브랜드별 종합 점수', fontsize=14, fontweight='bold')
        ax1.set_ylabel('점수 (1-5)', fontsize=11)
        ax1.set_ylim(0, 5.5)
        ax1.grid(axis='y', alpha=0.3)

        # 2. 통계 요약 텍스트
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        summary_text = f"""
테스트 결과 요약

총 메시지: {len(self.df)}개

평균 점수:
• 브랜드 톤: {self.df['score_brand_tone'].mean():.2f}
• 페르소나 적합: {self.df['score_persona_fit'].mean():.2f}
• 자연스러움: {self.df['score_naturalness'].mean():.2f}
• 구매 유도력: {self.df['score_purchase_motivation'].mean():.2f}
• 종합: {self.df['score_overall'].mean():.2f}

제약 통과율:
• 전체: {self.df['constraints_all_met'].sum() / len(self.df) * 100:.1f}%

평균 생성 시간:
• {self.df['generation_time_sec'].mean():.2f}초
        """
        ax2.text(0.1, 0.5, summary_text, fontsize=10, verticalalignment='center', family='monospace')

        # 3. 메시지 목적별 점수
        ax3 = fig.add_subplot(gs[1, :2])
        purpose_overall = self.df.groupby('message_purpose')['score_overall'].mean()
        purpose_overall.plot(kind='bar', ax=ax3, color='coral', edgecolor='black')
        ax3.set_title('메시지 목적별 종합 점수', fontsize=14, fontweight='bold')
        ax3.set_ylabel('점수 (1-5)', fontsize=11)
        ax3.set_ylim(0, 5.5)
        ax3.grid(axis='y', alpha=0.3)

        # 4. 제약 조건 통과율
        ax4 = fig.add_subplot(gs[1, 2])
        all_valid = self.df['constraints_all_met'].value_counts()
        ax4.pie(all_valid, labels=['통과', '실패'], autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
        ax4.set_title('전체 제약 조건', fontsize=12, fontweight='bold')

        # 5. 톤 일관성 (브랜드별)
        ax5 = fig.add_subplot(gs[2, :2])
        tone_by_brand = self.df.groupby('brand')['tone_consistency'].mean().sort_values(ascending=False)
        tone_by_brand.plot(kind='bar', ax=ax5, color='mediumseagreen', edgecolor='black')
        ax5.set_title('브랜드별 톤 일관성', fontsize=14, fontweight='bold')
        ax5.set_ylabel('일관성 점수 (0-1)', fontsize=11)
        ax5.set_ylim(0, 1.0)
        ax5.grid(axis='y', alpha=0.3)

        # 6. 생성 시간 분포
        ax6 = fig.add_subplot(gs[2, 2])
        ax6.hist(self.df['generation_time_sec'], bins=15, edgecolor='black', alpha=0.7, color='skyblue')
        ax6.axvline(self.df['generation_time_sec'].mean(), color='red', linestyle='--', linewidth=2)
        ax6.set_title('생성 시간 분포', fontsize=12, fontweight='bold')
        ax6.set_xlabel('시간 (초)', fontsize=10)
        ax6.set_ylabel('빈도', fontsize=10)

        fig.suptitle('아모레퍼시픽 CRM 마케팅 메시지 생성 시스템 - 종합 평가 대시보드', fontsize=18, fontweight='bold', y=0.98)

        plt.savefig(self.plots_dir / '08_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  [8/8] 종합 대시보드 저장")

    def show_top_messages(self, n: int = 5):
        """상위 N개 메시지 출력"""
        print("\n" + "="*60)
        print(f"평가 점수 상위 {n}개 메시지")
        print("="*60)

        top_messages = self.df.nlargest(n, 'score_overall')

        for idx, row in top_messages.iterrows():
            print(f"\n[{row['score_overall']:.2f}점] {row['brand']} - {row['message_purpose']}")
            print(f"페르소나: {row['persona_name']} ({row['age']}세, {row['occupation']})")
            print(f"제목: {row['title']}")
            print(f"본문: {row['body'][:100]}...")
            print("-" * 60)


def main():
    """메인 실행 함수"""

    visualizer = ResultVisualizer()

    # 대시보드 생성
    visualizer.create_dashboard()

    # 상위 메시지 출력
    visualizer.show_top_messages(n=3)

    print(f"\n모든 시각화 파일이 저장되었습니다:")
    print(f"  {visualizer.plots_dir.absolute()}")


if __name__ == "__main__":
    main()
