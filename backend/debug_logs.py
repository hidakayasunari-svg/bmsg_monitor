from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv("backend/.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("--- System Logs (Latest 10) ---")
logs = supabase.table("system_logs").select("*").order("created_at", desc=True).limit(10).execute()
for log in logs.data:
    print(f"[{log['created_at']}] {log['level']}: {log['message']}")

print("\n--- System Commands (Latest 5) ---")
cmds = supabase.table("system_commands").select("*").order("created_at", desc=True).limit(5).execute()
for cmd in cmds.data:
    print(f"[{cmd['created_at']}] {cmd['command']}: {cmd['status']}")
