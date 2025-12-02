"""
Pipeline Management Service
Handles deal stages, movements, and Kanban-style workflow
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PipelineService:
    """Manage sales pipeline and deal stages"""
    
    # Default pipeline stages
    DEFAULT_STAGES = [
        {
            'id': 'new_lead',
            'name': 'Nieuwe Lead',
            'order': 1,
            'color': '#3b82f6',  # blue
            'description': 'Net toegevoegd, nog geen contact'
        },
        {
            'id': 'contacted',
            'name': 'Contact Gemaakt',
            'order': 2,
            'color': '#8b5cf6',  # purple
            'description': 'Eerste email/call verzonden'
        },
        {
            'id': 'interested',
            'name': 'Interesse Getoond',
            'order': 3,
            'color': '#f59e0b',  # amber
            'description': 'Email geopend of geklikt'
        },
        {
            'id': 'meeting_scheduled',
            'name': 'Afspraak Gepland',
            'order': 4,
            'color': '#10b981',  # green
            'description': 'Demo of gesprek ingepland'
        },
        {
            'id': 'proposal_sent',
            'name': 'Offerte Verstuurd',
            'order': 5,
            'color': '#06b6d4',  # cyan
            'description': 'Voorstel/contract verzonden'
        },
        {
            'id': 'negotiation',
            'name': 'Onderhandeling',
            'order': 6,
            'color': '#f97316',  # orange
            'description': 'In gesprek over voorwaarden'
        },
        {
            'id': 'won',
            'name': '✅ Gewonnen',
            'order': 7,
            'color': '#22c55e',  # success green
            'description': 'Deal gesloten - klant!'
        },
        {
            'id': 'lost',
            'name': '❌ Verloren',
            'order': 8,
            'color': '#ef4444',  # red
            'description': 'Niet geïnteresseerd of verloren'
        }
    ]
    
    @classmethod
    def get_stages(cls) -> List[Dict]:
        """Get all pipeline stages"""
        return cls.DEFAULT_STAGES
    
    @classmethod
    def get_stage_by_id(cls, stage_id: str) -> Optional[Dict]:
        """Get specific stage"""
        for stage in cls.DEFAULT_STAGES:
            if stage['id'] == stage_id:
                return stage
        return None
    
    @classmethod
    def move_deal(cls, practice: Dict, to_stage: str, reason: str = None) -> Dict:
        """
        Move a practice/deal to a new pipeline stage
        
        Args:
            practice: Practice data
            to_stage: Target stage ID
            reason: Optional reason for the move
        
        Returns:
            Updated practice with pipeline data
        """
        stage = cls.get_stage_by_id(to_stage)
        if not stage:
            raise ValueError(f"Invalid stage: {to_stage}")
        
        # Initialize pipeline data if not exists
        if 'pipeline' not in practice:
            practice['pipeline'] = {
                'current_stage': 'new_lead',
                'history': [],
                'deal_value': 0,
                'probability': 0,
                'expected_close_date': None
            }
        
        # Record stage change
        old_stage = practice['pipeline'].get('current_stage', 'new_lead')
        
        if old_stage != to_stage:
            practice['pipeline']['history'].append({
                'from_stage': old_stage,
                'to_stage': to_stage,
                'moved_at': datetime.now().isoformat(),
                'reason': reason
            })
        
        # Update current stage
        practice['pipeline']['current_stage'] = to_stage
        practice['pipeline']['stage_entered_at'] = datetime.now().isoformat()
        
        # Update probability based on stage
        probability_map = {
            'new_lead': 5,
            'contacted': 10,
            'interested': 25,
            'meeting_scheduled': 50,
            'proposal_sent': 70,
            'negotiation': 85,
            'won': 100,
            'lost': 0
        }
        practice['pipeline']['probability'] = probability_map.get(to_stage, 0)
        
        # Update workflow status for backward compatibility
        if 'workflow' not in practice:
            practice['workflow'] = {}
        practice['workflow']['status'] = stage['name']
        
        logger.info(f"Moved practice {practice.get('nr')} from {old_stage} to {to_stage}")
        
        return practice
    
    @classmethod
    def auto_stage_from_activity(cls, practice: Dict, activity: str) -> Dict:
        """
        Automatically move deal based on activity
        
        Activities:
        - email_sent: → contacted
        - email_opened: → interested
        - email_clicked: → interested
        - email_replied: → meeting_scheduled
        - meeting_booked: → meeting_scheduled
        - proposal_sent: → proposal_sent
        - deal_won: → won
        - deal_lost: → lost
        """
        workflow = practice.get('workflow', {})
        current_stage = practice.get('pipeline', {}).get('current_stage', 'new_lead')
        
        # Define activity → stage mappings
        stage_transitions = {
            'email_sent': 'contacted',
            'email_opened': 'interested',
            'email_clicked': 'interested',
            'email_replied': 'meeting_scheduled',
            'meeting_booked': 'meeting_scheduled',
            'proposal_sent': 'proposal_sent',
            'deal_won': 'won',
            'deal_lost': 'lost'
        }
        
        target_stage = stage_transitions.get(activity)
        
        if target_stage:
            # Only move forward, never backward (except won/lost)
            stage_order = {s['id']: s['order'] for s in cls.DEFAULT_STAGES}
            current_order = stage_order.get(current_stage, 0)
            target_order = stage_order.get(target_stage, 0)
            
            if target_stage in ['won', 'lost'] or target_order > current_order:
                return cls.move_deal(
                    practice,
                    target_stage,
                    reason=f"Auto-moved based on activity: {activity}"
                )
        
        return practice
    
    @classmethod
    def get_pipeline_summary(cls, practices: List[Dict]) -> Dict:
        """
        Get summary of all deals in pipeline
        
        Returns:
            {
                'total_deals': int,
                'total_value': float,
                'stages': {
                    'new_lead': {'count': int, 'value': float},
                    ...
                },
                'conversion_rates': {...},
                'average_deal_age': float
            }
        """
        summary = {
            'total_deals': len(practices),
            'total_value': 0,
            'stages': {},
            'conversion_rates': {},
            'won_count': 0,
            'lost_count': 0
        }
        
        # Initialize stage counts
        for stage in cls.DEFAULT_STAGES:
            summary['stages'][stage['id']] = {
                'count': 0,
                'value': 0,
                'deals': []
            }
        
        # Count deals per stage
        for practice in practices:
            pipeline = practice.get('pipeline', {})
            current_stage = pipeline.get('current_stage', 'new_lead')
            deal_value = pipeline.get('deal_value', 0)
            
            if current_stage in summary['stages']:
                summary['stages'][current_stage]['count'] += 1
                summary['stages'][current_stage]['value'] += deal_value
                summary['stages'][current_stage]['deals'].append(practice.get('nr'))
                summary['total_value'] += deal_value
            
            if current_stage == 'won':
                summary['won_count'] += 1
            elif current_stage == 'lost':
                summary['lost_count'] += 1
        
        # Calculate conversion rates
        total_deals = len(practices)
        if total_deals > 0:
            summary['win_rate'] = (summary['won_count'] / total_deals) * 100
            summary['loss_rate'] = (summary['lost_count'] / total_deals) * 100
        
        return summary
    
    @classmethod
    def get_stalled_deals(cls, practices: List[Dict], days: int = 7) -> List[Dict]:
        """
        Find deals that haven't moved in X days
        """
        stalled = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for practice in practices:
            pipeline = practice.get('pipeline', {})
            stage_entered = pipeline.get('stage_entered_at')
            current_stage = pipeline.get('current_stage', 'new_lead')
            
            # Skip won/lost deals
            if current_stage in ['won', 'lost']:
                continue
            
            if stage_entered:
                try:
                    entered_date = datetime.fromisoformat(stage_entered.replace('Z', '+00:00'))
                    if entered_date.replace(tzinfo=None) < cutoff:
                        days_stalled = (datetime.now() - entered_date.replace(tzinfo=None)).days
                        practice['days_in_stage'] = days_stalled
                        stalled.append(practice)
                except Exception as e:
                    logger.error(f"Error checking stalled deal: {e}")
        
        return sorted(stalled, key=lambda x: x.get('days_in_stage', 0), reverse=True)
    
    @classmethod
    def forecast_revenue(cls, practices: List[Dict]) -> Dict:
        """
        Forecast expected revenue based on deal values and probabilities
        """
        forecast = {
            'total_pipeline_value': 0,
            'weighted_value': 0,
            'expected_wins': 0,
            'by_stage': {}
        }
        
        for practice in practices:
            pipeline = practice.get('pipeline', {})
            current_stage = pipeline.get('current_stage', 'new_lead')
            deal_value = pipeline.get('deal_value', 0)
            probability = pipeline.get('probability', 0) / 100
            
            # Skip won/lost
            if current_stage in ['won', 'lost']:
                continue
            
            forecast['total_pipeline_value'] += deal_value
            forecast['weighted_value'] += deal_value * probability
            
            if current_stage not in forecast['by_stage']:
                forecast['by_stage'][current_stage] = {
                    'total_value': 0,
                    'weighted_value': 0,
                    'deal_count': 0
                }
            
            forecast['by_stage'][current_stage]['total_value'] += deal_value
            forecast['by_stage'][current_stage]['weighted_value'] += deal_value * probability
            forecast['by_stage'][current_stage]['deal_count'] += 1
        
        return forecast


from datetime import timedelta
