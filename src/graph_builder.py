"""
LangGraph 워크플로우 구축
노드들을 연결하여 메시지 생성 파이프라인 구성
"""

from langgraph.graph import StateGraph, END
from .graph_nodes import MessageGenerationState, GraphNodes


def build_message_generation_graph(db_path: str, vector_manager):
    """메시지 생성 그래프 구축"""

    # 노드 초기화
    nodes = GraphNodes(db_path, vector_manager)

    # StateGraph 생성
    workflow = StateGraph(MessageGenerationState)

    # 노드 추가
    workflow.add_node("persona_analyzer", nodes.persona_analyzer)
    workflow.add_node("brand_selector", nodes.brand_selector)
    workflow.add_node("product_retriever", nodes.product_retriever)
    workflow.add_node("review_enricher", nodes.review_context_enricher)
    workflow.add_node("tone_adapter", nodes.tone_adapter)
    workflow.add_node("message_generator", nodes.message_generator)
    workflow.add_node("quality_validator", nodes.quality_validator)

    # 엣지 추가 (워크플로우 정의)
    workflow.set_entry_point("persona_analyzer")
    workflow.add_edge("persona_analyzer", "brand_selector")
    workflow.add_edge("brand_selector", "product_retriever")
    workflow.add_edge("product_retriever", "review_enricher")
    workflow.add_edge("review_enricher", "tone_adapter")
    workflow.add_edge("tone_adapter", "message_generator")
    workflow.add_edge("message_generator", "quality_validator")

    # 조건부 엣지: 검증 결과에 따라 재생성 or 종료
    def should_regenerate(state):
        """검증 실패 시 1회에 한해 재생성, 성공 시 종료"""
        # 1. 이미 검증 통과했으면 종료
        if state.get('is_valid', True):
            return "end"

        # 2. 검증 실패 시, 재시도 횟수 확인
        # (quality_validator에서 이미 1을 증가시켜서 보냄)
        current_retry = state.get('retry_count', 0)

        if current_retry == 1:
            # 첫 번째 실패임 -> 재시도
            print("\n[Self-Correction] 품질 기준 미달로 재생성을 시도합니다...")
            return "regenerate"
        else:
            # 두 번째 실패(1 초과) -> 포기하고 종료
            print("  [Stop] 재시도 횟수 초과로 프로세스를 종료합니다.")
            return "end"

    workflow.add_conditional_edges(
        "quality_validator",
        should_regenerate,
        {
            "regenerate": "message_generator",
            "end": END
        }
    )

    # 그래프 컴파일
    app = workflow.compile()

    return app
