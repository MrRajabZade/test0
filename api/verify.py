from http.server import BaseHTTPRequestHandler
import json, hmac, hashlib
from urllib.parse import parse_qs
from supabase_client import supabase

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            raw_data = self.rfile.read(content_length).decode('utf-8')
            
            # دیباگ: نمایش داده ورودی
            print(f"Raw input data: {raw_data}")
            
            post_data = parse_qs(raw_data)
            print(f"Parsed data: {post_data}")
            
            json_data = post_data.get('json', [''])[0]
            input_key = post_data.get('key', [''])[0]
            auto_save = post_data.get('auto_save', ['off'])[0].lower() == 'on'

            if not json_data or not input_key:
                raise ValueError("Missing required parameters")

            # اعتبارسنجی
            secret = "ValidateWebAppData"
            data = json.loads(json_data)
            sorted_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
            generated_key = hmac.new(secret.encode(), sorted_json.encode(), hashlib.sha256).hexdigest()

            is_valid = hmac.compare_digest(generated_key, input_key)

            # ذخیره خودکار اگر فعال باشد
            save_status = False
            if is_valid and auto_save:
                try:
                    user_data = data.get('user', {})
                    response = supabase.table('telegram_auth').insert({
                        "auth_data": data.get('auth_data'),
                        "chat_instance": data.get('chat_instance'),
                        "chat_type": data.get('chat_type'),
                        "device_id": data.get('device_id'),
                        "query_id": data.get('query_id'),
                        "platform": data.get('platform'),
                        "hash": generated_key,  # استفاده از کلید تولید شده
                        "user_id": user_data.get('id'),
                        "first_name": user_data.get('first_name'),
                        "last_name": user_data.get('last_name', ''),
                        "language_code": user_data.get('language_code', 'fa'),
                        "allows_write_to_pm": user_data.get('allows_write_to_pm', False),
                        "start_param": data.get('start_param', '')
                    }).execute()
                    save_status = True
                except Exception as db_error:
                    print("Database Error:", str(db_error))
                    # همچنان ادامه می‌دهیم حتی اگر ذخیره نشد

            response_data = {
                "valid": is_valid,
                "saved": save_status,
                "received_auto_save": auto_save  # برای دیباگ
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except json.JSONDecodeError as je:
            self.send_error(400, explain=f"Invalid JSON: {str(je)}")
        except Exception as e:
            self.send_error(400, explain=str(e))
