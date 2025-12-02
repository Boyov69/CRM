"""
Automation Engine
Intelligent follow-up system based on triggers and user behavior
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AutomationEngine:
    """AI-powered automation for follow-ups and actions"""
    
    # Automation rules configuration
    RULES = {
        'email_opened_no_click': {
            'trigger': 'email_opened',
            'condition': lambda p: not p.get('workflow', {}).get('email_clicked'),
            'wait_days': 2,
            'action': 'send_follow_up',
            'template': 'interest_detected',
            'priority': 'medium'
        },
        'email_clicked_no_reply': {
            'trigger': 'email_clicked',
            'condition': lambda p: not p.get('workflow', {}).get('replied'),
            'wait_days': 1,
            'action': 'send_follow_up',
            'template': 'high_interest',
            'priority': 'high'
        },
        'no_response_after_send': {
            'trigger': 'email_sent',
            'condition': lambda p: not p.get('workflow', {}).get('email_opened'),
            'wait_days': 5,
            'action': 'send_follow_up',
            'template': 'gentle_reminder',
            'priority': 'low'
        },
        'opened_multiple_times': {
            'trigger': 'email_opened',
            'condition': lambda p: p.get('workflow', {}).get('open_count', 0) >= 3,
            'wait_days': 0,
            'action': 'notify_sales',
            'priority': 'urgent'
        },
        'long_inactive': {
            'trigger': 'time_based',
            'condition': lambda p: True,
            'wait_days': 14,
            'action': 'send_reengagement',
            'template': 're_engagement',
            'priority': 'low'
        },
        'hot_lead_no_contact': {
            'trigger': 'score_based',
            'condition': lambda p: p.get('score', {}).get('total_score', 0) >= 75,
            'wait_days': 3,
            'action': 'notify_sales',
            'priority': 'urgent'
        }
    }
    
    @classmethod
    def check_triggers(cls, practice: Dict, event: str) -> List[Dict]:
        """
        Check if any automation rules should trigger
        
        Args:
            practice: Practice data
            event: Event that occurred (email_opened, email_clicked, etc.)
        
        Returns:
            List of actions to execute
        """
        actions = []
        workflow = practice.get('workflow', {})
        
        for rule_name, rule in cls.RULES.items():
            # Check if this rule applies to the event
            if rule['trigger'] != event and rule['trigger'] not in ['time_based', 'score_based']:
                continue
            
            # Check condition
            try:
                if rule['condition'](practice):
                    # Check if we should wait
                    should_execute, reason = cls._should_execute_now(
                        practice,
                        rule_name,
                        rule['wait_days']
                    )
                    
                    if should_execute:
                        action = {
                            'rule': rule_name,
                            'action_type': rule['action'],
                            'template': rule.get('template'),
                            'priority': rule['priority'],
                            'scheduled_for': datetime.now().isoformat(),
                            'reason': reason,
                            'practice_id': practice.get('nr')
                        }
                        actions.append(action)
                        logger.info(f"Triggered rule '{rule_name}' for practice {practice.get('nr')}")
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_name}: {e}")
        
        return actions
    
    @classmethod
    def _should_execute_now(cls, practice: Dict, rule_name: str, wait_days: int) -> tuple:
        """
        Check if enough time has passed to execute the rule
        
        Returns:
            (should_execute: bool, reason: str)
        """
        workflow = practice.get('workflow', {})
        
        # Check if rule was already executed
        automation_history = workflow.get('automation_history', [])
        last_execution = None
        
        for execution in automation_history:
            if execution.get('rule') == rule_name:
                last_execution = execution
                break
        
        # If never executed, check wait time from last email
        if not last_execution:
            last_email_date = workflow.get('last_email_date')
            if not last_email_date:
                return True, "First execution"
            
            try:
                last_date = datetime.fromisoformat(last_email_date.replace('Z', '+00:00'))
                days_since = (datetime.now() - last_date.replace(tzinfo=None)).days
                
                if days_since >= wait_days:
                    return True, f"{days_since} days since last email"
                else:
                    return False, f"Waiting {wait_days - days_since} more days"
            except:
                return True, "Could not determine last email date"
        
        # If executed before, check cooldown period (double the wait time)
        try:
            last_exec_date = datetime.fromisoformat(last_execution['executed_at'].replace('Z', '+00:00'))
            days_since_exec = (datetime.now() - last_exec_date.replace(tzinfo=None)).days
            cooldown = wait_days * 2
            
            if days_since_exec >= cooldown:
                return True, f"{days_since_exec} days since last execution"
            else:
                return False, f"In cooldown period ({cooldown - days_since_exec} days remaining)"
        except:
            return True, "Could not determine last execution"
    
    @classmethod
    def execute_action(cls, action: Dict, practice: Dict) -> Dict:
        """
        Execute an automation action
        
        Returns:
            Result of action execution
        """
        action_type = action['action_type']
        
        result = {
            'success': False,
            'action': action,
            'executed_at': datetime.now().isoformat(),
            'message': ''
        }
        
        try:
            if action_type == 'send_follow_up':
                result = cls._send_follow_up_email(practice, action)
            
            elif action_type == 'notify_sales':
                result = cls._notify_sales_team(practice, action)
            
            elif action_type == 'send_reengagement':
                result = cls._send_reengagement_email(practice, action)
            
            elif action_type == 'update_score':
                result = cls._update_lead_score(practice, action)
            
            else:
                result['message'] = f"Unknown action type: {action_type}"
                logger.warning(result['message'])
            
            # Record in automation history
            if 'workflow' not in practice:
                practice['workflow'] = {}
            
            if 'automation_history' not in practice['workflow']:
                practice['workflow']['automation_history'] = []
            
            practice['workflow']['automation_history'].append({
                'rule': action['rule'],
                'action': action_type,
                'executed_at': result['executed_at'],
                'success': result['success'],
                'message': result['message']
            })
            
        except Exception as e:
            result['message'] = f"Error executing action: {str(e)}"
            logger.error(result['message'])
        
        return result
    
    @classmethod
    def _send_follow_up_email(cls, practice: Dict, action: Dict) -> Dict:
        """Send automated follow-up email"""
        from backend.services.email_service import EmailService
        
        result = {
            'success': False,
            'executed_at': datetime.now().isoformat(),
            'message': ''
        }
        
        try:
            email_service = EmailService()
            template = action.get('template', 'follow_up')
            
            success = email_service.send_campaign_email(
                practice=practice,
                template_type=template,
                use_ai=True  # Use AI for automated emails
            )
            
            if success:
                result['success'] = True
                result['message'] = f"Sent {template} email to {practice.get('email')}"
                logger.info(result['message'])
                
                # Update workflow
                if 'workflow' not in practice:
                    practice['workflow'] = {}
                
                practice['workflow']['last_automated_email'] = datetime.now().isoformat()
                practice['workflow']['automated_emails_sent'] = \
                    practice['workflow'].get('automated_emails_sent', 0) + 1
            else:
                result['message'] = "Failed to send email"
        
        except Exception as e:
            result['message'] = f"Email send error: {str(e)}"
            logger.error(result['message'])
        
        return result
    
    @classmethod
    def _notify_sales_team(cls, practice: Dict, action: Dict) -> Dict:
        """Notify sales team about hot lead or action needed"""
        from backend.services.slack_service import SlackService
        
        result = {
            'success': False,
            'executed_at': datetime.now().isoformat(),
            'message': ''
        }
        
        try:
            # Prepare notification message
            score = practice.get('score', {}).get('total_score', 0)
            message = f"""
🔥 **HOT LEAD ALERT!**

**Praktijk:** {practice.get('naam', 'Unknown')}
**Gemeente:** {practice.get('gemeente', 'Unknown')}
**Score:** {score}/100
**Status:** {practice.get('workflow', {}).get('status', 'Unknown')}
**Reason:** {action.get('reason', 'Automation triggered')}

**Next Action:** {practice.get('score', {}).get('next_action', 'Review lead')}

👉 Check CRM voor details
            """.strip()
            
            # Send Slack notification (if configured)
            slack = SlackService()
            slack_sent = slack.send_notification(message)
            
            # Could also send email to sales team here
            
            result['success'] = True
            result['message'] = "Sales team notified"
            logger.info(f"Notified sales team about practice {practice.get('nr')}")
            
        except Exception as e:
            result['message'] = f"Notification error: {str(e)}"
            logger.error(result['message'])
        
        return result
    
    @classmethod
    def _send_reengagement_email(cls, practice: Dict, action: Dict) -> Dict:
        """Send re-engagement email for inactive leads"""
        return cls._send_follow_up_email(practice, action)
    
    @classmethod
    def _update_lead_score(cls, practice: Dict, action: Dict) -> Dict:
        """Recalculate and update lead score"""
        from backend.services.lead_scoring import LeadScoringService
        
        result = {
            'success': False,
            'executed_at': datetime.now().isoformat(),
            'message': ''
        }
        
        try:
            score_data = LeadScoringService.calculate_score(practice)
            practice['score'] = score_data
            
            result['success'] = True
            result['message'] = f"Updated score to {score_data['total_score']}"
            logger.info(result['message'])
            
        except Exception as e:
            result['message'] = f"Score update error: {str(e)}"
            logger.error(result['message'])
        
        return result
    
    @classmethod
    def get_pending_actions(cls, practices: List[Dict]) -> List[Dict]:
        """
        Get all pending automated actions for all practices
        """
        all_actions = []
        
        for practice in practices:
            # Check time-based triggers
            actions = cls.check_triggers(practice, 'time_based')
            all_actions.extend(actions)
            
            # Check score-based triggers
            actions = cls.check_triggers(practice, 'score_based')
            all_actions.extend(actions)
        
        # Sort by priority
        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_actions.sort(key=lambda x: priority_order.get(x['priority'], 99))
        
        return all_actions
    
    @classmethod
    def process_event(cls, practice: Dict, event: str) -> Dict:
        """
        Process an event and trigger appropriate automations
        
        Events:
        - email_sent
        - email_opened
        - email_clicked
        - email_replied
        - meeting_booked
        - deal_won
        - deal_lost
        
        Returns:
            {
                'actions_triggered': int,
                'actions': List[Dict],
                'updated_practice': Dict
            }
        """
        logger.info(f"Processing event '{event}' for practice {practice.get('nr')}")
        
        # Check which rules should trigger
        actions = cls.check_triggers(practice, event)
        
        # Execute immediate actions
        executed_actions = []
        for action in actions:
            if action['priority'] == 'urgent':
                result = cls.execute_action(action, practice)
                executed_actions.append(result)
        
        return {
            'actions_triggered': len(actions),
            'actions': actions,
            'executed_actions': executed_actions,
            'updated_practice': practice
        }


class SlackService:
    """Placeholder for Slack notifications"""
    def send_notification(self, message: str) -> bool:
        # Implementation in modules/slack_notifications.py
        logger.info(f"Slack notification: {message[:100]}...")
        return True
