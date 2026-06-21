import tiktoken

class TokenVisualizer:
    """Visualizes how text is split into tokens.
    
    This class provides utilities for understanding tokenization
    by showing exactly how input text becomes tokens.
    """
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize with a specific encoding.
        
        Args:
            encoding_name: The tiktoken encoding to use.
                          cl100k_base is used by GPT-4 and GPT-3.5-turbo.
        """
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def visualize_tokens(self, text: str) -> list[dict]:
        """Show token IDs and their decoded text.
        
        Args:
            text: Input text to tokenize.
            
        Returns:
            List of dicts with token_id and token_text.
        """
        token_ids = self.encoding.encode(text)
        result = []
        for token_id in token_ids:
            token_bytes = self.encoding.decode_single_token_bytes(token_id)
            result.append({
                'token_id': token_id,
                'token_text': token_bytes.decode('utf-8', errors='replace')
            })
        return result
    
    def analyze_boundaries(self, text: str) -> list[dict]:
    
        tokens = self.encoding.encode(text)
        boundaries = []
        position = 0
        
        for token_id in tokens:
            token_bytes = self.encoding.decode_single_token_bytes(token_id)
            token_text = token_bytes.decode('utf-8', errors='replace')
            
            boundaries.append({
                'token_id': token_id,
                'text': token_text,
                'starts_with_space': token_text.startswith(' '),
                'is_punctuation': token_text.strip() in '.,!?;:',
                'char_position': position,
                'byte_length': len(token_bytes)
            })
            position += len(token_text)
        
        return boundaries

# Example usage
visualizer = TokenVisualizer()
tokens = visualizer.visualize_tokens("Hello, world!")
for t in tokens:
    print(f"ID: {t['token_id']:6d} -> '{t['token_text']}'")

tokens = visualizer.analyze_boundaries("Hello, world!")
for t in tokens:
    print(f"ID: {t['token_id']:6d} -> '{t['text']}'")

print("\n--- All Output Properties of analyze_boundaries ---")
result = visualizer.analyze_boundaries("Hello, world!")
for i, item in enumerate(result):
    print(f"\nToken {i}:")
    for key, value in item.items():
        print(f"  {key}: {value}")


def identify_special_tokens(encoding_name: str = "cl100k_base") -> dict:
    """Identify special tokens in a tokenizer vocabulary.
    
    Args:
        encoding_name: The encoding to examine.
        
    Returns:
        Dictionary of special token names and their IDs.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    special_tokens = {}
    
    # cl100k_base special tokens
    special_names = [
        '<|endoftext|>',
        '<|fim_prefix|>',
        '<|fim_middle|>',
        '<|fim_suffix|>',
        '<|endofprompt|>'
    ]
    
    for name in special_names:
        try:
            token_id = encoding.encode_single_token(name)
            special_tokens[name] = token_id
        except KeyError:
            pass  # Token not in vocabulary
    
    return special_tokens