from http.server import BaseHTTPRequestHandler
import json, hmac, hashlib
from urllib.parse import parse_qs
from supabase_client import supabase
from datetime import datetime

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
            post_data = parse_qs(self.rfile.read(content_length).decode('utf-8'))
            
            json_data = post_data.get('json', [''])[0]
            input_key = post_data.get('key', [''])[0]
            auto_save = post_data.get('auto_save', ['off'])[0].lower()

            if not json_data or not input_key:
                raise ValueError("Missing parameters")

            # اعتبارسنجی
            secret = "ValidateWebAppData"
            data = json.loads(json_data)
            sorted_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
            generated_key = hmac.new(secret.encode(), sorted_json.encode(), hashlib.sha256).hexdigest()

            is_valid = hmac.compare_digest(generated_key, input_key)
            saved = False
            if is_valid and auto_save == 'on':
                try:
                    user_data = data.get('user', {})

                    response = supabase.table('user_verifications').insert({
                        "created_at": datetime.now().isoformat(),
                        "auth_data": data.get("auth_data"),
                        "chat_instance": data.get("chat_instance"),
                        "chat_type": data.get("chat_type"),
                        "device_id": data.get("device_id"),
                        "query_id": data.get("query_id"),
                        "platform": data.get("platform"),
                        "hash": data.get("hash"),
                        "user_id": user_data.get("id"),
                        "first_name": user_data.get("first_name"),
                        "last_name": user_data.get("last_name"),
                        "language_code": user_data.get("language_code"),
                        "allows_write_to_pm": user_data.get("allows_write_to_pm", False),
                        "start_param": data.get("start_param")
                    }).execute()
                    
                    saved = True
                    
                except Exception as db_error:
                    print("Database Error:", str(db_error))
                    saved = False

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
            self.end_headers()
            self.wfile.write(json.dumps({
                "valid": is_valid,
                "saved": saved
            }).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
