import tiktoken

class TokenizerComparison:
    """Compare different tokenizer approaches.
    
    This class helps understand differences between tokenizer types
    by showing how the same text tokenizes differently.
    """
    
    def __init__(self):
        """Initialize with multiple tokenizers."""
        # GPT-4 tokenizer (BPE)
        self.gpt4_enc = tiktoken.get_encoding("cl100k_base")
        # GPT-2 tokenizer (older BPE)
        self.gpt2_enc = tiktoken.get_encoding("gpt2")
    
    def compare_encodings(self, text: str) -> dict:
        """Compare how different tokenizers encode the same text.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            Dictionary with token counts and details for each tokenizer.
        """
        gpt4_tokens = self.gpt4_enc.encode(text)
        gpt2_tokens = self.gpt2_enc.encode(text)
        
        return {
            'text': text,
            'gpt4': {
                'count': len(gpt4_tokens),
                'tokens': gpt4_tokens[:10],  # First 10 for preview
                'efficiency': len(text) / len(gpt4_tokens)
            },
            'gpt2': {
                'count': len(gpt2_tokens),
                'tokens': gpt2_tokens[:10],
                'efficiency': len(text) / len(gpt2_tokens)
            }
        }
    
    def analyze_vocabulary_coverage(self, texts: list[str]) -> dict:
        """Analyze how well vocabularies cover given texts.
        
        Args:
            texts: List of texts to analyze.
            
        Returns:
            Statistics about tokenization efficiency.
        """
        results = {
            'gpt4': {'total_tokens': 0, 'total_chars': 0},
            'gpt2': {'total_tokens': 0, 'total_chars': 0}
        }
        
        for text in texts:
            results['gpt4']['total_tokens'] += len(self.gpt4_enc.encode(text))
            results['gpt4']['total_chars'] += len(text)
            results['gpt2']['total_tokens'] += len(self.gpt2_enc.encode(text))
            results['gpt2']['total_chars'] += len(text)
        
        for enc in results:
            results[enc]['avg_chars_per_token'] = (
                results[enc]['total_chars'] / results[enc]['total_tokens']
            )
        
        return results


# Call and print the output
if __name__ == "__main__":
    comparison = TokenizerComparison()
    
    # Test text
    sample_text = "Hello, world! This is a test of different tokenizers. Let's see how they handle this text."
    
    print("=" * 60)
    print("TOKENIZER COMPARISON RESULTS")
    print("=" * 60)
    print()
    
    # Compare encodings for single text
    print("1. ENCODING COMPARISON FOR SINGLE TEXT:")
    print("-" * 60)
    result = comparison.compare_encodings(sample_text)
    print(f"Text: {result['text']}")
    print()
    print(f"GPT-4 (cl100k_base):")
    print(f"  - Token count: {result['gpt4']['count']}")
    print(f"  - First 10 tokens: {result['gpt4']['tokens']}")
    print(f"  - Efficiency (chars/token): {result['gpt4']['efficiency']:.2f}")
    print()
    print(f"GPT-2:")
    print(f"  - Token count: {result['gpt2']['count']}")
    print(f"  - First 10 tokens: {result['gpt2']['tokens']}")
    print(f"  - Efficiency (chars/token): {result['gpt2']['efficiency']:.2f}")
    print()
    
    # Analyze vocabulary coverage
    print("2. VOCABULARY COVERAGE ANALYSIS:")
    print("-" * 60)
    test_texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning and artificial intelligence are transformative technologies.",
        "🔥 Emoji test: Let's see how tokenizers handle special characters! 🚀"
    ]
    
    vocab_results = comparison.analyze_vocabulary_coverage(test_texts)
    
    for tokenizer_name in vocab_results:
        data = vocab_results[tokenizer_name]
        print(f"{tokenizer_name.upper()}:")
        print(f"  - Total chars: {data['total_chars']}")
        print(f"  - Total tokens: {data['total_tokens']}")
        print(f"  - Avg chars per token: {data['avg_chars_per_token']:.2f}")
    
    print()
    print("=" * 60)