from collections import Counter

class SimpleBPE:
    """A simplified BPE tokenizer implementation.
    
    This demonstrates the core BPE algorithm:
    1. Start with character-level tokens
    2. Find most frequent adjacent pair
    3. Merge that pair into a new token
    4. Repeat until vocabulary size is reached
    """
    
    def __init__(self):
        """Initialize with empty vocabulary."""
        self.vocab = {}  # token -> id mapping
        self.merges = []  # list of (pair, new_token) merges
    
    def get_pairs(self, tokens: list[str]) -> Counter:
        """Count adjacent token pairs.
        
        Args:
            tokens: List of current tokens.
            
        Returns:
            Counter of (token1, token2) pairs.
        """
        pairs = Counter()
        for i in range(len(tokens) - 1):
            pair = (tokens[i], tokens[i + 1])
            pairs[pair] += 1
        return pairs
    
    def merge_pair(self, tokens: list[str], pair: tuple) -> list[str]:
        """Merge all occurrences of a pair.
        
        Args:
            tokens: Current token list.
            pair: The (token1, token2) pair to merge.
            
        Returns:
            New token list with pairs merged.
        """
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == pair:
                new_tokens.append(pair[0] + pair[1])
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        return new_tokens
    
    def train(self, text: str, num_merges: int) -> None:
        """Train BPE on text for specified number of merges.
        
        Args:
            text: Training text.
            num_merges: Number of merge operations to perform.
        """
        # Start with character-level tokens
        tokens = list(text)
        
        for _ in range(num_merges):
            pairs = self.get_pairs(tokens)
            if not pairs:
                break
            
            # Find most frequent pair
            best_pair = pairs.most_common(1)[0][0]
            
            # Merge it
            tokens = self.merge_pair(tokens, best_pair)
            new_token = best_pair[0] + best_pair[1]
            self.merges.append((best_pair, new_token))
            
            print(f"Merged {best_pair} -> '{new_token}'")
    
    def analyze_vocabulary_coverage(self, vocab_size: int, tokens: list[str]) -> dict:
        """Analyze how vocabulary size affects token coverage.
        
        This demonstrates the trade-off between vocabulary size and
        tokenization efficiency for different text types.
        
        Args:
            vocab_size: Size of vocabulary to simulate.
            tokens: List of tokens to analyze.
            
        Returns:
            Coverage statistics.
        """
        total_tokens = len(tokens)
        unique_tokens = len(set(tokens))
        
        return {
            'total_tokens': total_tokens,
            'unique_tokens': unique_tokens,
            'compression_ratio': total_tokens if total_tokens > 0 else 0,
            'vocabulary_utilization': unique_tokens / vocab_size if vocab_size > 0 else 0
        }

def trace_bpe_merges(text: str, num_merges: int = 10) -> list[dict]:
    """Trace BPE merge operations step by step.
    
    Args:
        text: Input text to trace.
        num_merges: Number of merges to perform.
        
    Returns:
        List of merge operation details.
    """
    tokens = list(text)
    trace = [{'step': 0, 'tokens': tokens.copy(), 'merge': None}]
    
    for step in range(1, num_merges + 1):
        pairs = Counter()
        for i in range(len(tokens) - 1):
            pairs[(tokens[i], tokens[i + 1])] += 1
        
        if not pairs:
            break
            
        best_pair = pairs.most_common(1)[0][0]
        
        # Merge the pair
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == best_pair:
                new_tokens.append(best_pair[0] + best_pair[1])
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        
        tokens = new_tokens
        trace.append({
            'step': step,
            'tokens': tokens.copy(),
            'merge': f"{best_pair[0]}+{best_pair[1]} -> {best_pair[0]+best_pair[1]}"
        })
    
    return trace


if __name__ == "__main__":
    # Example usage
    text = "ababab"
    bpe = SimpleBPE()
    
    # Train with merges
    tokens = list(text)
    print(f"Initial tokens: {tokens}\n")
    
    for merge_num in range(3):
        pairs = bpe.get_pairs(tokens)
        
        print(f"=== Merge {merge_num + 1} ===")
        print(f"All pairs found:")
        for pair, count in sorted(pairs.items(), key=lambda x: -x[1]):
            print(f"  {pair}: {count}")
        
        if not pairs:
            break
        
        best_pair = pairs.most_common(1)[0][0]
        print(f"\nMost frequent pair: {best_pair}")
        tokens = bpe.merge_pair(tokens, best_pair)
        print(f"Tokens after merge: {tokens}\n")
    
    # Analyze vocabulary coverage
    print("=== Vocabulary Coverage Analysis ===")
    coverage = bpe.analyze_vocabulary_coverage(vocab_size=256, tokens=tokens)
    print(f"Total tokens: {coverage['total_tokens']}")
    print(f"Unique tokens: {coverage['unique_tokens']}")
    print(f"Compression ratio: {coverage['compression_ratio']}")
    print(f"Vocabulary utilization: {coverage['vocabulary_utilization']:.2%}")