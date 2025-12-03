# modules/slack_notifications.py
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)

class SlackNotifier:
    """
    Slack notificaties voor belangrijke CRM events
    """
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or Config.SLACK_WEBHOOK_URL
        self.enabled = bool(self.webhook_url)
        
        if not self.enabled:
            logger.warning("Slack webhook URL not configured - notifications disabled")
    
    def send_message(self, text: str, blocks: List[Dict] = None, 
                     attachments: List[Dict] = None) -> bool:
        """Verstuur basis Slack bericht"""
        if not self.enabled:
            return False
        
        try:
            payload = {'text': text}
            if blocks: payload['blocks'] = blocks
            if attachments: payload['attachments'] = attachments
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
    
    def notify_campaign_started(self, total_practices: int, test_mode: bool = False):
        """Notificatie wanneer campagne start"""
        emoji = "🧪" if test_mode else "🚀"
        mode = "TEST" if test_mode else "PRODUCTION"
        
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} Email Campaign Started ({mode})"}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*Practices:*\n{total_practices}"},
                {"type": "mrkdwn", "text": f"*Started:*\n{datetime.now().strftime('%H:%M')}"}
            ]}
        ]
        return self.send_message(f"Campaign started: {total_practices} practices", blocks=blocks)
    
    def notify_campaign_completed(self, results: Dict):
        """Notificatie met campagne resultaten"""
        success = results.get('sent', 0)
        failed = results.get('failed', 0)
        
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "✅ Campaign Completed"}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*Sent:*\n{success}"},
                {"type": "mrkdwn", "text": f"*Failed:*\n{failed}"}
            ]}
        ]
        return self.send_message(f"Campaign completed: {success} sent", blocks=blocks)

    def notify_new_response(self, response_data: Dict, practice_data: Dict):
        """Notificatie bij nieuwe email response"""
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": "📧 New Email Response"}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*Practice:*\n{practice_data.get('naam', 'Unknown')}"},
                {"type": "mrkdwn", "text": f"*Subject:*\n{response_data.get('subject', 'No Subject')}"}
            ]},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*Preview:*\n```{response_data.get('body', '')[:200]}...```"}}
        ]
        return self.send_message(f"New response from {practice_data.get('naam')}", blocks=blocks)

# Helper functions
def notify_campaign_started(total, test=False): return SlackNotifier().notify_campaign_started(total, test)
def notify_campaign_completed(results): return SlackNotifier().notify_campaign_completed(results)
def notify_new_response(resp, prac): return SlackNotifier().notify_new_response(resp, prac)
