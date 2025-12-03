# modules/analytics.py
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

class CRMAnalytics:
    """
    Geavanceerde analytics voor CRM campagnes
    """
    
    def __init__(self, practices_data):
        self.practices = practices_data
    
    def get_overview_stats(self):
        """
        Algemeen overzicht van campagne prestaties
        """
        total = len(self.practices)
        contacted = sum(1 for p in self.practices if p.get('status') != 'Nieuw')
        replied = sum(1 for p in self.practices if p.get('workflow', {}).get('replied'))
        converted = sum(1 for p in self.practices if p.get('status') == 'Klant')
        
        # Calculate rates
        contact_rate = (contacted / total * 100) if total > 0 else 0
        reply_rate = (replied / contacted * 100) if contacted > 0 else 0
        conversion_rate = (converted / contacted * 100) if contacted > 0 else 0
        
        return {
            'total_practices': total,
            'contacted': contacted,
            'replied': replied,
            'converted': converted,
            'rates': {
                'contact_rate': round(contact_rate, 1),
                'reply_rate': round(reply_rate, 1),
                'conversion_rate': round(conversion_rate, 1)
            }
        }
    
    def get_funnel_analysis(self):
        """
        Gedetailleerde funnel analyse
        """
        stages = {
            'Sent': 0,
            'Delivered': 0,
            'Opened': 0,
            'Clicked': 0,
            'Replied': 0,
            'Demo Booked': 0,
            'Closed Won': 0
        }
        
        for p in self.practices:
            wf = p.get('workflow', {})
            status = p.get('status')
            
            if wf.get('emails_sent', 0) > 0:
                stages['Sent'] += 1
                stages['Delivered'] += 1  # Aanname voor nu
            
            if wf.get('opened'):
                stages['Opened'] += 1
            
            if wf.get('clicked'):
                stages['Clicked'] += 1
                
            if wf.get('replied'):
                stages['Replied'] += 1
                
            if status == 'Demo':
                stages['Demo Booked'] += 1
                
            if status == 'Klant':
                stages['Closed Won'] += 1
        
        return stages
    
    def get_ab_test_results(self):
        """
        Resultaten van A/B tests
        """
        # Mock data structure for now, real implementation would aggregate from logs
        return {
            'Subject Line A': {'opens': 45, 'rate': '22%'},
            'Subject Line B': {'opens': 52, 'rate': '28%'},
            'Subject Line C': {'opens': 38, 'rate': '19%'}
        }
    
    def get_roi_projection(self):
        """
        Bereken verwachte opbrengst
        """
        avg_deal_value = 499 * 12  # Jaarwaarde
        stats = self.get_overview_stats()
        
        current_revenue = stats['converted'] * avg_deal_value
        pipeline_value = stats['replied'] * avg_deal_value * 0.2  # 20% slaging
        
        return {
            'current_arr': current_revenue,
            'pipeline_value': pipeline_value,
            'projected_arr': current_revenue + pipeline_value
        }

class RealtimeAnalytics:
    """
    Real-time statistieken voor dashboard
    """
    
    @staticmethod
    def get_live_activity_feed(limit=10):
        """
        Haal laatste activiteiten op
        """
        # In productie zou dit uit een database/log komen
        # Mock data voor demo
        activities = [
            {'type': 'reply', 'practice': 'Huisartsen De Brug', 'time': '10 min geleden'},
            {'type': 'open', 'practice': 'Praktijk West', 'time': '12 min geleden'},
            {'type': 'click', 'practice': 'Dr. Janssens', 'time': '15 min geleden'},
            {'type': 'sent', 'practice': 'Medisch Centrum Zuid', 'time': '18 min geleden'},
            {'type': 'open', 'practice': 'Groepspraktijk Gent', 'time': '22 min geleden'}
        ]
        return activities[:limit]
