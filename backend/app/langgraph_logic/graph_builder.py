from langgraph.graph import StateGraph, START, END

# 각 노드 함수들을 import
from app.langgraph_nodes.rag_node import check_rag_function
from app.langgraph_nodes.web_search_node import web_search_node
from app.langgraph_nodes.llm_generate_node import llm_generate_node
from app.langgraph_nodes.merge_node import merge_node


def build_graph():
    builder = StateGraph(dict)

    # 노드 추가
    builder.add_node("check_rag", check_rag_function)
    builder.add_node("web_search", web_search_node)
    builder.add_node("llm_generate", llm_generate_node)
    builder.add_node(
        "merge_results", merge_node
    )  # 노드 이름 변경 (merge는 예약어일 수 있음)

    # 시작 엣지
    builder.add_edge(START, "check_rag")

    # 조건부 엣지: check_rag 이후 라우팅
    def route_after_rag(state: dict):
        print(f"--- Router after RAG (State: {state}) ---")
        if state.get("error"):  # RAG 단계에서 에러 발생 시
            print("Routing to: merge_results (due to RAG error)")
            return "to_merge"  # 에러가 있어도 일단 merge로 보내서 처리된 부분까지 반환

        missing_web = state.get("missing_web", 0)
        missing_llm = state.get("missing_llm", 0)

        if missing_web == 0 and missing_llm == 0:  # RAG만으로 충분
            print("Routing to: merge_results (RAG sufficient)")
            return "to_merge"
        elif missing_web > 0:  # 웹 검색 필요
            print("Routing to: web_search")
            return "to_web_search"
        elif missing_llm > 0:  # 웹 검색 불필요, LLM 생성만 필요
            print("Routing to: llm_generate (skipping web)")
            return "to_llm_direct"
        else:  # 예상치 못한 경우, 일단 merge
            print("Routing to: merge_results (fallback from after_rag)")
            return "to_merge"

    builder.add_conditional_edges(
        "check_rag",
        route_after_rag,
        {
            "to_merge": "merge_results",
            "to_web_search": "web_search",
            "to_llm_direct": "llm_generate",  # RAG -> LLM 경로
        },
    )

    # 조건부 엣지: web_search 이후 라우팅
    def route_after_web(state: dict):
        print(f"--- Router after Web Search (State: {state}) ---")
        if state.get("error"):  # 웹 검색 단계에서 에러 발생 시
            print("Routing to: merge_results (due to web_search error)")
            return "to_merge"

        missing_llm = state.get("missing_llm", 0)
        if missing_llm > 0:  # LLM 생성 필요
            print("Routing to: llm_generate")
            return "to_llm"
        else:  # LLM 생성 불필요 (웹 검색으로 끝 또는 RAG+웹으로 충분)
            print("Routing to: merge_results (web_search sufficient or no llm needed)")
            return "to_merge"

    builder.add_conditional_edges(
        "web_search",
        route_after_web,
        {"to_llm": "llm_generate", "to_merge": "merge_results"},
    )

    # llm_generate 이후에는 항상 merge_results로
    builder.add_edge("llm_generate", "merge_results")

    # merge_results 이후에는 END
    builder.add_edge("merge_results", END)

    graph = builder.compile()
    print("LangGraph compiled successfully.")
    return graph


# 전역 그래프 인스턴스 (앱 시작 시 한 번 컴파일)
# 단, uvicorn --workers > 1 설정 시 각 워커마다 생성됨.
# FastAPI lifespan을 사용하거나 의존성 주입으로 관리하는 것이 더 좋음.
compiled_graph = build_graph()
