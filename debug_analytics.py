from modules.supabase_client import SupabaseDB
from modules.analytics import CRMAnalytics
import json

db = SupabaseDB()
practices = db.get_practices()
print(f"Loaded {len(practices)} practices")

if len(practices) > 0:
    print("Sample practice workflow:", json.dumps(practices[0].get('workflow', {}), indent=2))
    print("Sample practice status:", practices[0].get('status'))

analytics = CRMAnalytics(practices)
stats = analytics.get_overview_stats()
print("Analytics Stats:", json.dumps(stats, indent=2))
