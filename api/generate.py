from http.server import BaseHTTPRequestHandler
import json
import os

# Note: Vercel serverless functions have limitations
# This is a simplified version that uses external API calls
# For full functionality, you'll need to use Vercel's paid plan or alternative hosting

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            prompt = data.get('prompt', '')
            model = data.get('model', 'gemma3:4b')
            
            # CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Note: For production, you'll need to:
            # 1. Deploy Ollama on a separate server (e.g., Railway, Fly.io)
            # 2. Use Hugging Face Inference API
            # 3. Use OpenAI API with fine-tuned model
            
            # Placeholder response for now
            response = {
                "status": "success",
                "message": "This endpoint requires external AI service configuration",
                "note": "Please configure OLLAMA_API_URL environment variable or use alternative AI service",
                "model": model,
                "response": "Please configure the AI backend service. See deployment documentation."
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "message": str(e)
            }
            
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
