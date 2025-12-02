"""
Pipeline API endpoints
"""
from flask import Blueprint, jsonify, request
import logging

from backend.services.database import DatabaseService
from backend.services.pipeline import PipelineService
from backend.services.lead_scoring import LeadScoringService
from backend.services.automation_engine import AutomationEngine

pipeline_bp = Blueprint('pipeline', __name__)
logger = logging.getLogger(__name__)

db = DatabaseService()


@pipeline_bp.route('/pipeline/stages', methods=['GET'])
def get_stages():
    """Get all pipeline stages"""
    stages = PipelineService.get_stages()
    return jsonify(stages)


@pipeline_bp.route('/pipeline/summary', methods=['GET'])
def get_pipeline_summary():
    """Get pipeline summary with deal counts and values"""
    try:
        practices = db.get_practices()
        summary = PipelineService.get_pipeline_summary(practices)
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Pipeline summary error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/pipeline/deals', methods=['GET'])
def get_deals_by_stage():
    """Get all deals grouped by stage"""
    try:
        stage_id = request.args.get('stage')
        practices = db.get_practices()
        
        # Group by stage
        deals_by_stage = {}
        for stage in PipelineService.DEFAULT_STAGES:
            deals_by_stage[stage['id']] = []
        
        for practice in practices:
            current_stage = practice.get('pipeline', {}).get('current_stage', 'new_lead')
            if current_stage in deals_by_stage:
                deals_by_stage[current_stage].append(practice)
        
        if stage_id:
            return jsonify(deals_by_stage.get(stage_id, []))
        
        return jsonify(deals_by_stage)
    
    except Exception as e:
        logger.error(f"Get deals error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/pipeline/move', methods=['POST'])
def move_deal():
    """
    Move a deal to a new stage
    
    Body:
        {
            "practice_id": int,
            "to_stage": str,
            "reason": str (optional)
        }
    """
    try:
        data = request.json
        practice_id = data.get('practice_id')
        to_stage = data.get('to_stage')
        reason = data.get('reason')
        
        if not practice_id or not to_stage:
            return jsonify({'error': 'practice_id and to_stage required'}), 400
        
        # Get practice
        practice = db.get_practice(practice_id)
        if not practice:
            return jsonify({'error': 'Practice not found'}), 404
        
        # Move to new stage
        updated_practice = PipelineService.move_deal(practice, to_stage, reason)
        
        # Update lead score
        score_data = LeadScoringService.calculate_score(updated_practice)
        updated_practice['score'] = score_data
        
        # Save
        db.upsert_practice(updated_practice)
        
        return jsonify({
            'success': True,
            'practice': updated_practice,
            'message': f"Moved to {to_stage}"
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Move deal error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/pipeline/stalled', methods=['GET'])
def get_stalled_deals():
    """Get deals that haven't moved in X days"""
    try:
        days = int(request.args.get('days', 7))
        practices = db.get_practices()
        stalled = PipelineService.get_stalled_deals(practices, days)
        
        return jsonify({
            'count': len(stalled),
            'deals': stalled
        })
    except Exception as e:
        logger.error(f"Stalled deals error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/pipeline/forecast', methods=['GET'])
def get_revenue_forecast():
    """Get revenue forecast based on pipeline"""
    try:
        practices = db.get_practices()
        forecast = PipelineService.forecast_revenue(practices)
        return jsonify(forecast)
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/leads/score/<int:practice_id>', methods=['POST'])
def calculate_lead_score(practice_id):
    """Calculate/recalculate lead score for a practice"""
    try:
        practice = db.get_practice(practice_id)
        if not practice:
            return jsonify({'error': 'Practice not found'}), 404
        
        score_data = LeadScoringService.calculate_score(practice)
        practice['score'] = score_data
        
        db.upsert_practice(practice)
        
        return jsonify({
            'success': True,
            'score': score_data
        })
    except Exception as e:
        logger.error(f"Score calculation error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/leads/hot', methods=['GET'])
def get_hot_leads():
    """Get hot leads (score >= 75)"""
    try:
        limit = int(request.args.get('limit', 10))
        practices = db.get_practices()
        hot_leads = LeadScoringService.get_hot_leads(practices, limit)
        
        return jsonify({
            'count': len(hot_leads),
            'leads': hot_leads
        })
    except Exception as e:
        logger.error(f"Hot leads error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/leads/attention', methods=['GET'])
def get_leads_needing_attention():
    """Get leads that need immediate attention"""
    try:
        practices = db.get_practices()
        attention_leads = LeadScoringService.needs_attention(practices)
        
        return jsonify({
            'count': len(attention_leads),
            'leads': attention_leads
        })
    except Exception as e:
        logger.error(f"Attention leads error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/automation/trigger', methods=['POST'])
def trigger_automation():
    """
    Trigger automation based on an event
    
    Body:
        {
            "practice_id": int,
            "event": str (email_opened, email_clicked, etc.)
        }
    """
    try:
        data = request.json
        practice_id = data.get('practice_id')
        event = data.get('event')
        
        if not practice_id or not event:
            return jsonify({'error': 'practice_id and event required'}), 400
        
        practice = db.get_practice(practice_id)
        if not practice:
            return jsonify({'error': 'Practice not found'}), 404
        
        # Process event and trigger automations
        result = AutomationEngine.process_event(practice, event)
        
        # Save updated practice
        db.upsert_practice(result['updated_practice'])
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Automation trigger error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/automation/pending', methods=['GET'])
def get_pending_automations():
    """Get all pending automated actions"""
    try:
        practices = db.get_practices()
        pending_actions = AutomationEngine.get_pending_actions(practices)
        
        return jsonify({
            'count': len(pending_actions),
            'actions': pending_actions
        })
    except Exception as e:
        logger.error(f"Pending actions error: {e}")
        return jsonify({'error': str(e)}), 500


@pipeline_bp.route('/automation/execute', methods=['POST'])
def execute_automation():
    """
    Execute a specific automation action
    
    Body:
        {
            "practice_id": int,
            "action": {...}
        }
    """
    try:
        data = request.json
        practice_id = data.get('practice_id')
        action = data.get('action')
        
        if not practice_id or not action:
            return jsonify({'error': 'practice_id and action required'}), 400
        
        practice = db.get_practice(practice_id)
        if not practice:
            return jsonify({'error': 'Practice not found'}), 404
        
        # Execute action
        result = AutomationEngine.execute_action(action, practice)
        
        # Save updated practice
        db.upsert_practice(practice)
        
        return jsonify({
            'success': result['success'],
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Execute automation error: {e}")
        return jsonify({'error': str(e)}), 500
