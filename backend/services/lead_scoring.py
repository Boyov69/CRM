"""
Lead Scoring Service
Calculates lead quality based on engagement, demographics, and behavior
"""
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class LeadScoringService:
    """AI-powered lead scoring system"""
    
    # Scoring weights
    WEIGHTS = {
        'email_opened': 10,
        'email_clicked': 20,
        'email_replied': 30,
        'website_visit': 15,
        'phone_call': 25,
        'form_filled': 20,
        'meeting_booked': 40,
    }
    
    # Demographic weights
    DEMOGRAPHIC_SCORES = {
        'has_email': 10,
        'has_phone': 10,
        'has_website': 5,
        'practice_size_large': 15,
        'practice_size_medium': 10,
        'practice_size_small': 5,
    }
    
    # Time decay factors
    RECENCY_MULTIPLIERS = {
        'today': 1.5,
        'this_week': 1.2,
        'this_month': 1.0,
        'older': 0.7,
    }
    
    @classmethod
    def calculate_score(cls, practice: Dict) -> Dict:
        """
        Calculate comprehensive lead score
        
        Returns:
            {
                'total_score': int (0-100),
                'category': str ('hot', 'warm', 'cold'),
                'engagement_score': int,
                'demographic_score': int,
                'recency_score': float,
                'next_action': str,
                'priority': int (1-5)
            }
        """
        engagement = cls._calculate_engagement_score(practice)
        demographic = cls._calculate_demographic_score(practice)
        recency = cls._calculate_recency_multiplier(practice)
        
        # Total score with recency bonus
        total_score = int((engagement + demographic) * recency)
        total_score = min(100, max(0, total_score))  # Cap at 0-100
        
        # Determine category
        if total_score >= 75:
            category = 'hot'
            priority = 1
            next_action = '🔥 Bel onmiddellijk!'
        elif total_score >= 50:
            category = 'warm'
            priority = 2
            next_action = '📧 Stuur persoonlijke follow-up'
        elif total_score >= 25:
            category = 'cold'
            priority = 3
            next_action = '📅 Zet in nurture campagne'
        else:
            category = 'frozen'
            priority = 4
            next_action = '❄️ Wacht of markeer als verloren'
        
        return {
            'total_score': total_score,
            'category': category,
            'engagement_score': engagement,
            'demographic_score': demographic,
            'recency_multiplier': recency,
            'next_action': next_action,
            'priority': priority,
            'calculated_at': datetime.now().isoformat()
        }
    
    @classmethod
    def _calculate_engagement_score(cls, practice: Dict) -> int:
        """Calculate score based on engagement activities"""
        score = 0
        workflow = practice.get('workflow', {})
        
        # Email interactions
        if workflow.get('email_opened'):
            score += cls.WEIGHTS['email_opened']
        
        if workflow.get('email_clicked'):
            score += cls.WEIGHTS['email_clicked']
        
        if workflow.get('replied'):
            score += cls.WEIGHTS['email_replied']
        
        # Number of emails sent (diminishing returns)
        emails_sent = workflow.get('emails_sent', 0)
        if emails_sent > 0:
            score += min(emails_sent * 3, 15)  # Max 15 points
        
        # Call interactions
        if workflow.get('phone_contacted'):
            score += cls.WEIGHTS['phone_call']
        
        # Meeting booked
        if workflow.get('meeting_booked'):
            score += cls.WEIGHTS['meeting_booked']
        
        return min(score, 70)  # Max 70 from engagement
    
    @classmethod
    def _calculate_demographic_score(cls, practice: Dict) -> int:
        """Calculate score based on practice demographics"""
        score = 0
        
        # Contact info completeness
        if practice.get('email'):
            score += cls.DEMOGRAPHIC_SCORES['has_email']
        
        if practice.get('tel'):
            score += cls.DEMOGRAPHIC_SCORES['has_phone']
        
        if practice.get('website'):
            score += cls.DEMOGRAPHIC_SCORES['has_website']
        
        # Practice size (based on number of doctors)
        artsen = practice.get('artsen', [])
        if isinstance(artsen, list):
            if len(artsen) >= 5:
                score += cls.DEMOGRAPHIC_SCORES['practice_size_large']
            elif len(artsen) >= 2:
                score += cls.DEMOGRAPHIC_SCORES['practice_size_medium']
            else:
                score += cls.DEMOGRAPHIC_SCORES['practice_size_small']
        
        return min(score, 30)  # Max 30 from demographics
    
    @classmethod
    def _calculate_recency_multiplier(cls, practice: Dict) -> float:
        """Calculate multiplier based on recency of last interaction"""
        workflow = practice.get('workflow', {})
        last_email_date = workflow.get('last_email_date')
        
        if not last_email_date:
            return 0.5  # No recent activity
        
        try:
            last_date = datetime.fromisoformat(last_email_date.replace('Z', '+00:00'))
            days_ago = (datetime.now() - last_date.replace(tzinfo=None)).days
            
            if days_ago == 0:
                return cls.RECENCY_MULTIPLIERS['today']
            elif days_ago <= 7:
                return cls.RECENCY_MULTIPLIERS['this_week']
            elif days_ago <= 30:
                return cls.RECENCY_MULTIPLIERS['this_month']
            else:
                return cls.RECENCY_MULTIPLIERS['older']
        except Exception as e:
            logger.error(f"Error calculating recency: {e}")
            return 1.0
    
    @classmethod
    def bulk_score(cls, practices: List[Dict]) -> List[Dict]:
        """Score multiple practices and sort by score"""
        scored_practices = []
        
        for practice in practices:
            score_data = cls.calculate_score(practice)
            practice['score'] = score_data
            scored_practices.append(practice)
        
        # Sort by total score (highest first)
        scored_practices.sort(
            key=lambda x: x['score']['total_score'],
            reverse=True
        )
        
        return scored_practices
    
    @classmethod
    def get_hot_leads(cls, practices: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top hot leads"""
        scored = cls.bulk_score(practices)
        return [p for p in scored if p['score']['category'] == 'hot'][:limit]
    
    @classmethod
    def needs_attention(cls, practices: List[Dict]) -> List[Dict]:
        """
        Find leads that need immediate attention
        - High score but no recent contact
        - Warm leads going cold
        - Engaged but not followed up
        """
        attention_needed = []
        
        for practice in practices:
            score_data = cls.calculate_score(practice)
            workflow = practice.get('workflow', {})
            
            # High score but no recent contact (7+ days)
            last_email = workflow.get('last_email_date')
            if score_data['total_score'] >= 60 and last_email:
                try:
                    last_date = datetime.fromisoformat(last_email.replace('Z', '+00:00'))
                    days_ago = (datetime.now() - last_date.replace(tzinfo=None)).days
                    if days_ago >= 7:
                        practice['attention_reason'] = f'High score ({score_data["total_score"]}) but {days_ago} days since last contact'
                        practice['score'] = score_data
                        attention_needed.append(practice)
                except:
                    pass
            
            # Email opened but no follow-up
            if workflow.get('email_opened') and not workflow.get('replied') and workflow.get('emails_sent', 0) < 2:
                practice['attention_reason'] = 'Opened email but no follow-up sent'
                practice['score'] = score_data
                attention_needed.append(practice)
        
        return attention_needed
