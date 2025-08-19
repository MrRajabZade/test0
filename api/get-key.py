from http.server import BaseHTTPRequestHandler
import json, hmac, hashlib

ALLOWED_ORIGIN = "https://eitaabin.rozblog.com"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        if self.headers.get('Origin') == ALLOWED_ORIGIN:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        else:
            self.send_response(403)
            self.end_headers()
    
    def do_POST(self):
        try:
            origin = self.headers.get('Origin', '')
            if origin != ALLOWED_ORIGIN:
                self.send_response(403)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Access denied"}).encode())
                return
                
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            if not post_data.startswith('json='):
                raise ValueError("Invalid format. Use 'json={...}'")
            
            json_data = post_data[5:]  # حذف 'json='
            data = json.loads(json_data)

            # تولید کلید
            secret = "ValidateWebAppData"
            sorted_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
            generated_key = hmac.new(secret.encode(), sorted_json.encode(), hashlib.sha256).hexdigest()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"key": generated_key}).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
