"""Campaign management API endpoints"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

from backend.services.database import DatabaseService
from backend.services.email_service import EmailService
from backend.services.analytics import AnalyticsService

campaigns_bp = Blueprint('campaigns', __name__)
logger = logging.getLogger(__name__)

db = DatabaseService()
email_service = EmailService()
analytics = AnalyticsService()


@campaigns_bp.route('/campaign/start', methods=['POST'])
def start_campaign():
    """Start email campaign"""
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
                
                success = email_service.send_campaign_email(
                    practice=practice,
                    template_type=template_type,
                    use_ai=use_ai
                )
                
                if success:
                    results['sent'] += 1
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


@campaigns_bp.route('/campaign/stats', methods=['GET'])
def get_campaign_stats():
    """Get campaign statistics"""
    try:
        practices = db.get_practices()
        stats = analytics.get_stats(practices)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        # Fallback stats
        practices = db.get_practices()
        total = len(practices)
        contacted = len([p for p in practices if p.get('workflow', {}).get('emails_sent', 0) > 0])
        leads = len([p for p in practices if p.get('status') in ['Lead', 'Geïnteresseerd']])
        
        return jsonify({
            'overview': {
                'total': total,
                'contacted': contacted,
                'leads': leads,
                'conversion_rate': leads / contacted if contacted > 0 else 0
            },
            'funnel': {},
            'roi': {}
        })
