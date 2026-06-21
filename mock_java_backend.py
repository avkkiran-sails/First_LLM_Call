#!/usr/bin/env python
"""Mock Java backend server on port 8080 for testing"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MockJavaHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests to /search"""
        if self.path == "/search":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            
            try:
                data = json.loads(body)
                query = data.get('prompt', '')
                
                # Mock responses based on query
                responses = {
                    'mcp': 'MCP (Model Context Protocol) is an open protocol that standardizes how applications interact with LLMs and other AI services. It enables Claude and other AI systems to seamlessly access external tools, APIs, and data sources.',
                    'protocol': 'A protocol is a set of rules governing communication between systems. In AI context, protocols like MCP define how clients and servers exchange messages and data.',
                    'server': 'A server is a computer system that provides resources and services to clients. An MCP server exposes tools and data sources that AI clients can call and interact with.',
                }
                
                # Check if query contains key words
                response_text = 'No matching response found.'
                query_lower = query.lower()
                
                if 'model context protocol' in query_lower or 'mcp server' in query_lower:
                    response_text = 'In the context of AI, an MCP (Model Context Protocol) server is an application that implements the MCP standard to expose tools, resources, and capabilities to AI models like Claude. It enables:\n\n1. Tool Discovery: AI models can discover what tools and functions are available\n2. Tool Invocation: AI models can request the server to execute specific tools with parameters\n3. Real-time Data Access: Servers can provide current data and information to AI models\n4. Bidirectional Communication: Uses HTTP/SSE for reliable request-response cycles\n\nAn MCP server acts as a bridge between AI models and external systems, APIs, databases, or custom business logic. It standardizes how these interactions happen, making it easier to build AI-powered applications with access to real-time information and powerful external tools.'
                elif 'what is mcp' in query_lower:
                    response_text = responses['mcp']
                elif 'what is' in query_lower:
                    for keyword, resp in responses.items():
                        if keyword in query_lower:
                            response_text = resp
                            break
                
                # Return response
                response = {
                    'response': response_text,
                    'query': query,
                    'timestamp': '2026-06-09T16:00:00Z'
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests to /source/{id}"""
        if self.path.startswith("/source/"):
            source_id = self.path.split("/")[-1]
            response = {
                'id': source_id,
                'title': f'Source {source_id}',
                'content': f'This is the detailed content for source {source_id}.',
                'url': f'https://example.com/source/{source_id}'
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        return

if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 8081), MockJavaHandler)
    print("Mock Java backend running on http://127.0.0.1:8081")
    print("Endpoints:")
    print("  POST /search - Search endpoint")
    print("  GET /source/{id} - Source details endpoint")
    print("\nPress CTRL+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
