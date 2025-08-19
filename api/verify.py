from http.server import BaseHTTPRequestHandler
import json, hmac, hashlib
from urllib.parse import parse_qs
from supabase_client import save_to_db  # اینجا import شده

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
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

                    saved = save_to_db({
                        "auth_data": data.get("auth_data"),
                        "chat_instance": data.get("chat_instance"),
                        "chat_type": data.get("chat_type"),
                        "device_id": data.get("device_id"),
                        "query_id": data.get("query_id"),
                        "platform": data.get("platform"),
                        "hash": data.get("hash"),
                        "id": user_data.get("id"),
                        "first_name": user_data.get("first_name"),
                        "last_name": user_data.get("last_name"),
                        "language_code": user_data.get("language_code"),
                        "allows_write_to_pm": user_data.get("allows_write_to_pm", False),
                        "start_param": data.get("start_param")
                    })
                    
                except Exception as db_error:
                    print("Database Error:", str(db_error))
                    saved = False

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "valid": is_valid,
                "saved": saved,
                "auto_save_received": auto_save
            }).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
