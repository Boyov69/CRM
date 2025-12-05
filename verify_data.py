from modules.supabase_client import SupabaseDB
import json

db = SupabaseDB()
practices = db.get_practices()
print(f"Loaded {len(practices)} practices")
if len(practices) > 0:
    print("First practice keys:", practices[0].keys())
    print("First practice sample:", json.dumps(practices[0], indent=2))
else:
    print("No practices loaded")
