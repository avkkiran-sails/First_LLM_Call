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

# Example usage
visualizer = TokenVisualizer()
tokens = visualizer.visualize_tokens("Hello, world!")
for t in tokens:
    print(f"ID: {t['token_id']:6d} -> '{t['token_text']}'")
