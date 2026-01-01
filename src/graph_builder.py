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
        """검증 실패 시 재생성, 성공 시 종료"""
        if state.get('is_valid', True):
            return "end"
        else:
            # 간단히 종료 (실제로는 재생성 로직 추가 가능)
            return "end"

    workflow.add_conditional_edges(
        "quality_validator",
        should_regenerate,
        {
            "end": END
        }
    )

    # 그래프 컴파일
    app = workflow.compile()

    return app
