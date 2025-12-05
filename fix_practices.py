"""Quick fix to reload practices data"""
import sys
sys.path.insert(0, '.')

from backend.services.database import DatabaseService
import requests

# Test database
db = DatabaseService()
practices = db.get_practices()
print(f"✅ Database has {len(practices)} practices")

# Test API
try:
    response = requests.get('http://localhost:5000/api/practices')
    api_data = response.json()
    print(f"❌ API returns {len(api_data)} practices")
    
    if len(api_data) == 0 and len(practices) > 0:
        print("\n🔧 Issue: API niet gesynchroniseerd met database")
        print("💡 Oplossing: Server herstarten")
except Exception as e:
    print(f"❌ API error: {e}")
