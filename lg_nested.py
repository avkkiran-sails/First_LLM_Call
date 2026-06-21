from typing import TypedDict, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from operator import add

class SearchResult(TypedDict):
    """Single search result structure."""
    title: str
    url: str
    snippet: str
    relevance_score: float

class SearchContext(TypedDict):
    """Context for search operations."""
    query: str
    results: list[SearchResult]
    total_found: int
    search_time_ms: float

class ReasoningStep(TypedDict):
    """Single step in reasoning chain."""
    thought: str
    action: str
    observation: str

class ReasoningContext(TypedDict):
    """Context for reasoning operations."""
    steps: list[ReasoningStep]
    current_hypothesis: str
    confidence: float

class NestedAgentState(TypedDict):
    """Agent state with nested structures."""
    # Top-level identifiers
    task_id: str
    user_query: str

    # Nested contexts
    search: SearchContext
    reasoning: ReasoningContext

    # Accumulating log
    action_log: Annotated[list[str], add]

    # Final output
    response: Optional[str]

def search_node(state: NestedAgentState) -> dict:
    """Perform search and update nested search context."""
    query = state["user_query"]

    # Simulate search results
    mock_results = [
        SearchResult(
            title=f"Result for {query}",
            url="https://example.com/1",
            snippet=f"Information about {query}...",
            relevance_score=0.95
        )
    ]

    return {
        "search": {
            "query": query,
            "results": mock_results,
            "total_found": len(mock_results),
            "search_time_ms": 150.5
        },
        "action_log": [f"Searched for: {query}"]
    }

def reason_node(state: NestedAgentState) -> dict:
    """Process search results and update reasoning context."""
    search_results = state["search"]["results"]

    step = ReasoningStep(
        thought=f"Found {len(search_results)} results to analyze",
        action="Synthesize information",
        observation="Results are relevant to query"
    )

    return {
        "reasoning": {
            "steps": [step],
            "current_hypothesis": "Query can be answered from search results",
            "confidence": 0.85
        },
        "action_log": ["Completed reasoning step"]
    }

# Build graph with nested state
nested_graph = StateGraph(NestedAgentState)
nested_graph.add_node("search", search_node)
nested_graph.add_node("reason", reason_node)
nested_graph.add_edge(START, "search")
nested_graph.add_edge("search", "reason")
nested_graph.add_edge("reason", END)
compiled_nested = nested_graph.compile()

# Execute with nested initial state
result = compiled_nested.invoke({
    "task_id": "task-001",
    "user_query": "What is LangGraph?",
    "search": {"query": "", "results": [], "total_found": 0, "search_time_ms": 0},
    "reasoning": {"steps": [], "current_hypothesis": "", "confidence": 0.0},
    "action_log": [],
    "response": None
})

print(f"Search found: {result['search']['total_found']} results")
print(f"Reasoning confidence: {result['reasoning']['confidence']}")
print(f"Action log: {result['action_log']}")
print(f"Final response: {result['response']}")

# Verify that the action log accumulated correctly
print(f"Action log length: {len(result['action_log'])}")
print(f"Action log: {result['action_log']}")