from flask import Flask, render_template, jsonify, request, send_file
import json
import os
import csv
import logging
from datetime import datetime
from config import Config
from modules.email_templates import EmailTemplates
from modules.sendgrid_integration import SendGridEmailService
from modules.ai_email_generator import AIEmailGenerator
from modules.response_tracker import GmailResponseTracker
from modules.analytics import CRMAnalytics
from modules.supabase_client import SupabaseDB
from huisartsen_scraper import get_website_and_email, search_leads

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=Config.LOG_FILE)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
email_service = SendGridEmailService()
response_tracker = GmailResponseTracker()
db = SupabaseDB()

DATA_FILE = Config.DATA_FILE  # Kept for backwards compatibility

# --- HELPER FUNCTIONS ---
def load_data():
    """Fallback: Load from JSON if DB unavailable"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    """Fallback: Save to JSON for backup"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/practices', methods=['GET'])
def get_practices():
    data = db.get_practices() # Use Supabase to get practices
    
    # Normalize data for frontend
    for p in data:
        # Map 'gem' to 'gemeente' if missing
        if 'gemeente' not in p and 'gem' in p:
            p['gemeente'] = p['gem']
            
        # Ensure 'naam' uses 'praktijk' if available and 'naam' is generic or missing
        if 'praktijk' in p and (not p.get('naam') or p.get('naam') == 'Team'):
            p['naam'] = p['praktijk']
            
        # Map 'notitie' to 'adres' if 'adres' is missing (heuristic)
        if 'adres' not in p and 'notitie' in p:
            p['adres'] = p['notitie']
            
    return jsonify(data)

@app.route('/api/practices', methods=['POST'])
def add_practice():
    new_practice = request.json
    
    # Generate ID if not present (Supabase usually handles this, but for consistency with existing logic)
    # We'll let the frontend or DB handle ID generation if possible, or fetch max ID.
    # For now, we assume the frontend sends a 'nr' or we generate one.
    if 'nr' not in new_practice:
        # Simple max ID fetch (inefficient but works for small datasets)
        all_practices = db.get_practices()
        max_id = max([p.get('nr', 0) for p in all_practices]) if all_practices else 0
        new_practice['nr'] = max_id + 1
        
    # Add workflow defaults
    if 'workflow' not in new_practice:
        new_practice['workflow'] = {
            'emails_sent': 0,
            'last_contact': None,
            'status': 'Nieuw',
            'next_action': 'Initial Outreach'
        }
        
    success = db.upsert_practice(new_practice) # Use Supabase to save practice
    if success:
        return jsonify(new_practice), 201
    return jsonify({'error': 'Failed to save practice'}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_practice():
    # Expects JSON: { "naam": "...", "gemeente": "..." }
    req_data = request.json
    naam = req_data.get('naam')
    gemeente = req_data.get('gemeente')

    if not naam or not gemeente:
        return jsonify({"error": "Naam en Gemeente verplicht"}), 400

    print(f"Scraping request voor: {naam}, {gemeente}")
    website, email, phone, riziv, doctors = get_website_and_email(naam, gemeente)

    return jsonify({
        "website": website,
        "email": email,
        "tel": phone,
        "riziv": riziv,
        "artsen": doctors
    })

@app.route('/api/leads', methods=['POST'])
def find_leads():
    req_data = request.json
    gemeente = req_data.get('gemeente')

    if not gemeente:
        return jsonify({"error": "Gemeente verplicht"}), 400

    leads = search_leads(gemeente)
    return jsonify(leads)

@app.route('/api/campaign/start', methods=['POST'])
def start_campaign():
    """Start de email campagne voor geselecteerde praktijken"""
    try:
        data = db.get_practices()
        target_ids = request.json.get('ids', [])
        template_type = request.json.get('template', 'initial_outreach')
        use_ai = request.json.get('use_ai', False)
        
        results = {
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        practices_to_update = []
        
        for practice in data:
            if str(practice.get('nr')) in map(str, target_ids):
                email = practice.get('email')
                if not email:
                    continue
                
                # Genereer email content
                if use_ai:
                    email_content = AIEmailGenerator.generate_personalized_email(
                        practice, template_type
                    )
                else:
                    email_content = EmailTemplates.get_template(
                        template_type, practice
                    )
                
                # Verstuur email
                success, response = email_service.send_email(
                    to_email=email,
                    subject=email_content['subject'],
                    body_text=email_content['body'],
                    body_html=email_content.get('html'),
                    custom_args={'practice_id': practice['nr']}
                )
                
                if success:
                    results['sent'] += 1
                    # Update workflow status
                    if 'workflow' not in practice:
                        practice['workflow'] = {}
                    
                    practice['workflow'].update({
                        'last_email_date': datetime.now().isoformat(),
                        'last_email_template': template_type,
                        'emails_sent': practice['workflow'].get('emails_sent', 0) + 1,
                        'status': 'Contacted'
                    })
                    practices_to_update.append(practice)
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'id': practice['nr'],
                    'success': success,
                    'email': email
                })
        
        if practices_to_update:
            db.bulk_upsert(practices_to_update)
            
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Campaign error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/stats', methods=['GET'])
def get_campaign_stats():
    """Haal campagne statistieken op"""
    data = db.get_practices()
    print(f"DEBUG: get_campaign_stats loaded {len(data)} practices")
    
    analytics = CRMAnalytics(data)
    
    stats = analytics.get_overview_stats()
    print(f"DEBUG: get_campaign_stats stats: {stats}")
    
    funnel = analytics.get_funnel_analysis()
    roi = analytics.get_roi_projection()
    
    return jsonify({
        'overview': stats,
        'funnel': funnel,
        'roi': roi
    })

@app.route('/api/practice/<id>/mark-replied', methods=['POST'])
def mark_replied(id):
    """Markeer een praktijk als 'heeft geantwoord'"""
    # Note: id is string in URL but usually int in DB. 
    # We'll try to convert or use string matching.
    try:
        practice_id = int(id)
    except ValueError:
        return jsonify({'error': 'Invalid ID'}), 400

    practice = db.get_practice(practice_id)
    
    if practice:
        if 'workflow' not in practice:
            practice['workflow'] = {}
        
        practice['workflow']['replied'] = True
        practice['workflow']['reply_date'] = datetime.now().isoformat()
        practice['status'] = 'Lead'
        
        db.upsert_practice(practice)
        return jsonify({'status': 'success'})
        
    return jsonify({'error': 'Practice not found'}), 404

if __name__ == '__main__':
    # Ensure data and logs directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Create empty data file if not exists (backup)
    if not os.path.exists(DATA_FILE):
        save_data([])
        
    app.run(debug=True, port=5000)
