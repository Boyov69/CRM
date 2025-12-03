import requests
import argparse
import sys

def run_campaign(api_url, template, use_ai):
    print(f"🚀 Start campagne...")
    print(f"Template: {template}")
    print(f"AI Mode: {'AAN' if use_ai else 'UIT'}")
    
    try:
        # Stap 1: Haal practices op
        print("Ophalen praktijken...")
        practices_resp = requests.get(f"{api_url}/api/practices")
        practices = practices_resp.json()
        
        # Filter op status 'Nieuw' of 'Contacted'
        target_ids = [p['nr'] for p in practices if p.get('status') in ['Nieuw', 'Contacted']]
        
        if not target_ids:
            print("Geen praktijken gevonden om te mailen.")
            return
            
        print(f"🎯 {len(target_ids)} praktijken geselecteerd.")
        
        # Stap 2: Start campagne
        payload = {
            'ids': target_ids,
            'template': template,
            'use_ai': use_ai
        }
        
        resp = requests.post(f"{api_url}/api/campaign/start", json=payload)
        result = resp.json()
        
        print("--------------------------------")
        print(f"✅ Verzonden: {result.get('sent', 0)}")
        print(f"❌ Mislukt: {result.get('failed', 0)}")
        print("--------------------------------")
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CRM Campaign')
    parser.add_argument('--url', default='http://localhost:5000', help='API URL')
    parser.add_argument('--template', default='initial_outreach', help='Email template type')
    parser.add_argument('--ai', action='store_true', help='Use AI generation')
    
    args = parser.parse_args()
    
    run_campaign(args.url, args.template, args.ai)
