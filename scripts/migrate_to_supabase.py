# scripts/migrate_to_supabase.py
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.supabase_client import SupabaseDB
from config import Config

def migrate():
    print("🚀 Starting migration to Supabase...")
    
    # Load JSON data
    json_path = Config.DATA_FILE
    if not os.path.exists(json_path):
        print(f"❌ Data file not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print(f"📦 Found {len(data)} practices in JSON.")
    
    # Init Supabase
    db = SupabaseDB()
    if not db.client:
        print("❌ Supabase client not initialized. Check credentials.")
        return
    
    # Prepare data for Supabase
    # Ensure keys match DB columns
    practices_to_upsert = []
    for item in data:
        practice = {
            'nr': item.get('nr'),
            'naam': item.get('naam'),
            'praktijk': item.get('praktijk'),
            'gem': item.get('gem'),
            'adres': item.get('adres'),
            'email': item.get('email'),
            'tel': item.get('tel'),
            'status': item.get('status'),
            'notitie': item.get('notitie'),
            'artsen_namen': item.get('artsen_namen'),
            'riziv': item.get('riziv'),
            'workflow': item.get('workflow', {})
        }
        practices_to_upsert.append(practice)
    
    # Batch upsert (Supabase has limits on payload size, so batching is safer)
    batch_size = 100
    total_migrated = 0
    
    for i in range(0, len(practices_to_upsert), batch_size):
        batch = practices_to_upsert[i:i+batch_size]
        success = db.bulk_upsert(batch)
        if success:
            total_migrated += len(batch)
            print(f"✅ Migrated batch {i}-{i+len(batch)}")
        else:
            print(f"❌ Failed to migrate batch {i}-{i+len(batch)}")
            
    print(f"🎉 Migration complete. Total: {total_migrated}")

if __name__ == "__main__":
    migrate()
