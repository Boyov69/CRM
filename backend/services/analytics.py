"""Analytics service"""
from typing import List, Dict


class AnalyticsService:
    """Analytics and reporting service"""
    
    def get_stats(self, practices: List[Dict]) -> Dict:
        """Get campaign statistics"""
        from modules.analytics import CRMAnalytics
        
        analytics = CRMAnalytics(practices)
        
        return {
            'overview': analytics.get_overview_stats(),
            'funnel': analytics.get_funnel_analysis(),
            'roi': analytics.get_roi_projection()
        }
