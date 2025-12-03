"""Test Flask app startup with Sprint 2 blueprints"""
import sys
sys.path.insert(0, '.')

print("🧪 Testing Flask App Startup...\n")

try:
    from flask import Flask
    print("✅ Flask imported")
    
    # Create test app
    app = Flask(__name__)
    print("✅ Flask app created")
    
    # Test blueprint registration
    from backend.api import register_blueprints
    register_blueprints(app)
    print("✅ Blueprints registered")
    
    # List all registered blueprints
    print("\n📋 Registered Blueprints:")
    for bp_name, bp in app.blueprints.items():
        print(f"   • {bp_name}: {bp.url_prefix}")
    
    # List Sprint 2 routes
    print("\n📋 Sprint 2 Routes:")
    sprint2_routes = [rule for rule in app.url_map.iter_rules() 
                     if any(x in rule.rule for x in ['/sms', '/whatsapp', '/inbox'])]
    
    for route in sorted(sprint2_routes, key=lambda x: x.rule):
        methods = ','.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
        print(f"   • {methods:12} {route.rule}")
    
    print("\n✅ Flask app startup successful!")
    print(f"✅ Total routes: {len(list(app.url_map.iter_rules()))}")
    print(f"✅ Sprint 2 routes: {len(sprint2_routes)}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

