from dataclasses import dataclass
from enum import Enum
from typing import Dict, List
import tiktoken

@dataclass
class ContextAllocation:
    system_prompt: int = 0
    conversation: int = 0
    retrieval: int = 0
    tools: int = 0

    @property
    def total(self) -> int:
        return (
            self.system_prompt
            + self.conversation
            + self.retrieval
            + self.tools
        )

class ContextStrategy(Enum):
    CONVERSATION_HEAVY = "conversation_heavy"
    RETRIEVAL_HEAVY = "retrieval_heavy"
    BALANCED = "balanced"
    MINIMAL = "minimal"

STRATEGY_SPLITS = {
    ContextStrategy.CONVERSATION_HEAVY: (0.15, 0.60, 0.15, 0.10),
    ContextStrategy.RETRIEVAL_HEAVY:    (0.10, 0.25, 0.55, 0.10),
    ContextStrategy.BALANCED:           (0.15, 0.35, 0.35, 0.15),
    ContextStrategy.MINIMAL:            (0.20, 0.20, 0.30, 0.10),
}

class ContextBudgetManager:
    def __init__(
        self,
        total_tokens: int = 8000,
        output_reserve: int = 1000,
        strategy: ContextStrategy = ContextStrategy.BALANCED,
    ):
        self.total_tokens = total_tokens
        self.output_reserve = output_reserve
        available = total_tokens - output_reserve
        sp, conv, ret, tools = STRATEGY_SPLITS[strategy]
        self.budget = {
            "system_prompt": int(available * sp),
            "conversation": int(available * conv),
            "retrieval":    int(available * ret),
            "tools":        int(available * tools),
        }
        self.allocation = ContextAllocation()

    def can_allocate(self, category: str, tokens: int) -> bool:
        used = getattr(self.allocation, category)
        within_category = used + tokens <= self.budget[category]
        within_total = (
            self.allocation.total + tokens
            <= self.total_tokens - self.output_reserve
        )
        return within_category and within_total

    def allocate(self, category: str, tokens: int) -> bool:
        if not self.can_allocate(category, tokens):
            return False
        setattr(
            self.allocation,
            category,
            getattr(self.allocation, category) + tokens,
        )
        return True

    def utilization(self) -> Dict[str, float]:
        return {
            cat: getattr(self.allocation, cat) / max(1, b)
            for cat, b in self.budget.items()
        }

class TokenCounter:
    def __init__(self, model: str = "gpt-4"):
        try:
            self._encoder = tiktoken.encoding_for_model(model)
        except Exception:
            self._encoder = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        return len(self._encoder.encode(text or ""))

    def count_messages(self, messages: List[dict]) -> int:
        # 4 tokens of overhead per message + 3 for conversation markers
        return 3 + sum(
            4
            + self.count(m.get("role", ""))
            + self.count(m.get("content", ""))
            for m in messages
        )

# Assuming your classes (ContextAllocation, ContextStrategy, ContextBudgetManager, TokenCounter) 
# are already defined above.

if __name__ == "__main__":
    print("--- Initializing Token Manager ---")
    # Initialize the manager with a total of 8000 tokens, 1000 reserved for output,
    # and using the BALANCED strategy.
    manager = ContextBudgetManager(total_tokens=8000, output_reserve=1000, strategy=ContextStrategy.BALANCED)
    counter = TokenCounter(model="gpt-4")

    # Print the initial calculated budget limits for each category
    print(f"Total Available Input Tokens: {manager.total_tokens - manager.output_reserve}")
    for category, budget_limit in manager.budget.items():
        print(f"  - Budget for {category:<15}: {budget_limit} tokens")
    print("-" * 35)

    # 1. Simulate a System Prompt
    system_text = "You are a helpful assistant specialized in analyzing financial data."
    system_tokens = counter.count(system_text)
    print(f"\n[System Prompt] Calculated tokens: {system_tokens}")
    
    if manager.allocate("system_prompt", system_tokens):
        print(f"Successfully allocated {system_tokens} tokens to system_prompt.")
    else:
        print("Allocation failed for system_prompt!")

    # 2. Simulate Chat Messages (Conversation History)
    mock_messages = [
        {"role": "user", "content": "Can you check my quarterly budget trends?"},
        {"role": "assistant", "content": "Sure, please provide the latest data points."},
        {"role": "user", "content": "Here is the summary: Q1 revenue was up by 12%."}
    ]
    conversation_tokens = counter.count_messages(mock_messages)
    print(f"\n[Conversation History] Calculated overhead + content tokens: {conversation_tokens}")

    if manager.can_allocate("conversation", conversation_tokens):
        manager.allocate("conversation", conversation_tokens)
        print(f"Successfully allocated {conversation_tokens} tokens to conversation.")
    else:
        print("Warning: Conversation exceeds allocated category budget!")

    # 3. Simulate Large Retrieval Context (e.g., RAG documents)
    # Let's try to allocate a large block to see how the budget safety checks perform
    retrieved_chunk = "Company Financials Report 2026: " + "Lorem ipsum dolor sit amet. " * 150
    retrieval_tokens = counter.count(retrieved_chunk)
    print(f"\n[Retrieval Documents] Calculated tokens: {retrieval_tokens}")

    # Check if it fits before attempting allocation
    if manager.can_allocate("retrieval", retrieval_tokens):
        manager.allocate("retrieval", retrieval_tokens)
        print(f"Successfully allocated {retrieval_tokens} tokens to retrieval.")
    else:
        print(f"Allocation REJECTED for retrieval. {retrieval_tokens} tokens exceeds the budget cap of {manager.budget['retrieval']}.")

    # 4. Final Summary and Utilization Report
    print("\n" + "="*40)
    print("FINAL CONTEXT UTILIATION SUMMARY")
    print("="*40)
    print(f"Total Tokens Allocated: {manager.allocation.total} / {manager.total_tokens - manager.output_reserve}")
    
    utilization_rates = manager.utilization()
    for cat, rate in utilization_rates.items():
        used = getattr(manager.allocation, cat)
        cap = manager.budget[cat]
        print(f"{cat:<15}: Used {used:>4} / {cap:>4} ({rate * 100:.2f}%)")
    print("="*40)