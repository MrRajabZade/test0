from http.server import BaseHTTPRequestHandler
import json, hmac, hashlib

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:    
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
