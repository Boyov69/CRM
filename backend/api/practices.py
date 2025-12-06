"""Practice management API endpoints"""
from flask import Blueprint, jsonify, request
from datetime import datetime

from backend.services.database import DatabaseService

practices_bp = Blueprint('practices', __name__)
db = DatabaseService()


@practices_bp.route('/practices', methods=['GET'])
def get_practices():
    """Get all practices"""
    practices = db.get_practices()
    
    # Normalize data for frontend
    for p in practices:
        # Map 'gem' to 'gemeente' if missing
        if 'gemeente' not in p and 'gem' in p:
            p['gemeente'] = p['gem']
            
        # Ensure 'naam' uses 'praktijk' if available and 'naam' is generic or missing
        if 'praktijk' in p and (not p.get('naam') or p.get('naam') == 'Team'):
            p['naam'] = p['praktijk']
            
        # Map 'notitie' to 'adres' if 'adres' is missing (heuristic)
        if 'adres' not in p and 'notitie' in p:
            p['adres'] = p['notitie']

    return jsonify(practices)


@practices_bp.route('/practices', methods=['POST'])
def add_practice():
    """Add new practice"""
    new_practice = request.json
    
    if 'nr' not in new_practice:
        all_practices = db.get_practices()
        max_id = max([p.get('nr', 0) for p in all_practices]) if all_practices else 0
        new_practice['nr'] = max_id + 1
    
    if 'workflow' not in new_practice:
        new_practice['workflow'] = {
            'emails_sent': 0,
            'last_contact': None,
            'status': 'Nieuw',
            'next_action': 'Initial Outreach'
        }
    
    success = db.upsert_practice(new_practice)
    if success:
        return jsonify(new_practice), 201
    return jsonify({'error': 'Failed to save practice'}), 500


@practices_bp.route('/practices/<int:practice_id>', methods=['GET'])
def get_practice(practice_id):
    """Get specific practice"""
    practice = db.get_practice(practice_id)
    if practice:
        return jsonify(practice)
    return jsonify({'error': 'Practice not found'}), 404


@practices_bp.route('/practices/<int:practice_id>', methods=['PUT'])
def update_practice(practice_id):
    """Update practice"""
    practice = db.get_practice(practice_id)
    if not practice:
        return jsonify({'error': 'Practice not found'}), 404
    
    updates = request.json
    practice.update(updates)
    
    success = db.upsert_practice(practice)
    if success:
        return jsonify(practice)
    return jsonify({'error': 'Failed to update practice'}), 500


@practices_bp.route('/practices/<int:practice_id>', methods=['DELETE'])
def delete_practice(practice_id):
    """Delete practice"""
    practice = db.get_practice(practice_id)
    if not practice:
        return jsonify({'error': 'Practice not found'}), 404
    
    success = db.delete_practice(practice_id)
    if success:
        return jsonify({'status': 'success', 'message': 'Practice deleted'})
    return jsonify({'error': 'Failed to delete practice'}), 500


@practices_bp.route('/practices/<int:practice_id>/mark-replied', methods=['POST'])
def mark_replied(practice_id):
    """Mark practice as replied"""
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
