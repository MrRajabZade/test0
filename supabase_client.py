from supabase import create_client
import os

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

# اضافه کردن خط زیر برای دیباگ
print(f"Connecting to Supabase at: {url}")  # این خط را اضافه کنید

supabase = create_client(url, key)

def save_to_db(data):
    return supabase.table('user_verifications').insert(data).execute()
