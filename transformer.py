"""
Visualizing the core transformer concept.

This example demonstrates how attention weights represent
relationships between tokens in a sequence.
"""

import numpy as np
from typing import List, Dict

def softmax(x: np.ndarray) -> np.ndarray:
    """Apply softmax to get attention weights."""
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)


def visualize_attention_concept(
    tokens: List[str],
    query_idx: int
) -> Dict[str, float]:
    """
    Demonstrate the attention concept with a simplified example.

    In real transformers, attention scores come from learned
    query-key dot products. Here we simulate to show the concept.

    Args:
        tokens: List of tokens in the sequence
        query_idx: Which token is querying for information​‍​‍﻿﻿‍‌﻿‍‍​‍﻿﻿﻿‌​﻿﻿‍​​‌﻿﻿‌‌‍​‍​

    Returns:
        Dict mapping each token to its attention weight
    """
    n_tokens = len(tokens)

    # Simulated attention scores (in reality, from Q*K^T)
    # Higher scores for semantically related tokens
    raw_scores = np.random.randn(n_tokens)

    # Apply softmax to get attention weights that sum to 1
    attention_weights = softmax(raw_scores)

    # Create readable output
    attention_map = {
        token: float(weight)
        for token, weight in zip(tokens, attention_weights)
    }

    return attention_map


# Example usage
tokens = ["The", "cat", "sat", "on", "the", "mat"]
attention = visualize_attention_concept(tokens, query_idx=1)

print(f"Token 'cat' attends to other tokens:")
for token, weight in attention.items():
    bar = "#" * int(weight * 50)
    print(f"  {token:6s}: {weight:.3f} {bar}")