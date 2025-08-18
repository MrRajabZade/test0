from http.server import BaseHTTPRequestHandler
import json, hmac, hashlib
from urllib.parse import parse_qs
from supabase_client import supabase

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = parse_qs(self.rfile.read(content_length).decode('utf-8'))
            
            json_data = post_data.get('json', [''])[0]
            input_key = post_data.get('key', [''])[0]

            if not json_data or not input_key:
                raise ValueError("Missing parameters")

            # اعتبارسنجی
            secret = "ValidateWebAppData"
            data = json.loads(json_data)
            sorted_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
            generated_key = hmac.new(secret.encode(), sorted_json.encode(), hashlib.sha256).hexdigest()

            is_valid = hmac.compare_digest(generated_key, input_key)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"valid": is_valid}).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
