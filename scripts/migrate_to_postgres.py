# scripts/migrate_to_postgres.py
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.models import Practice, init_db
from config import Config

def migrate():
    print("🚀 Starting migration to PostgreSQL...")
    
    # Load JSON data
    json_path = Config.DATA_FILE
    if not os.path.exists(json_path):
        print(f"❌ Data file not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print(f"📦 Found {len(data)} practices in JSON.")
    
    # Init DB
    session = init_db()
    
    count = 0
    for item in data:
        # Check if exists
        exists = session.query(Practice).filter_by(nr=item.get('nr')).first()
        if exists:
            continue
            
        practice = Practice(
            nr=item.get('nr'),
            naam=item.get('naam'),
            praktijk=item.get('praktijk'),
            gem=item.get('gem'),
            adres=item.get('adres'),
            email=item.get('email'),
            tel=item.get('tel'),
            status=item.get('status'),
            notitie=item.get('notitie'),
            artsen_namen=item.get('artsen_namen'),
            riziv=item.get('riziv'),
            workflow=item.get('workflow', {})
        )
        session.add(practice)
        count += 1
    
    session.commit()
    print(f"✅ Migrated {count} new practices to database.")

if __name__ == "__main__":
    migrate()
