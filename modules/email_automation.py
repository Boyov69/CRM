# modules/email_automation.py
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from config import Config
from modules.email_templates import EmailTemplates
from modules.sendgrid_integration import SendGridEmailService
from modules.ai_email_generator import AIEmailGenerator
from modules.supabase_client import SupabaseDB

logger = logging.getLogger(__name__)

class EmailAutomationEngine:
    """
    Centrale email automation engine
    Ondersteunt meerdere providers: SendGrid, Gmail SMTP, Custom SMTP
    """
    
    def __init__(self):
        self.provider = Config.EMAIL_PROVIDER
        self.daily_limit = Config.DAILY_EMAIL_LIMIT
        self.rate_limit = Config.EMAILS_PER_MINUTE
        self.emails_sent_today = 0
        self.last_send_time = None
        self.db = SupabaseDB()
        
        # Initialize email service based on provider
        if self.provider == 'sendgrid':
            self.email_service = SendGridEmailService()
        else:
            # Fallback to SMTP (mock for now if not implemented)
            self.email_service = SendGridEmailService() 
        
        logger.info(f"Email engine initialized with provider: {self.provider}")
    
    def process_campaign(self, practices_data: List[Dict], force_send: bool = False) -> Dict:
        """
        Verwerkt de volledige email campagne
        """
        today = datetime.now().date()
        results = {
            'success_count': 0,
            'failed_count': 0,
            'skipped_count': 0,
            'results': [],
            'processing_time': 0
        }
        
        start_time = time.time()
        
        # Filter practices die email nodig hebben
        practices_to_email = self._filter_practices_for_campaign(practices_data, today)
        
        logger.info(f"Starting campaign for {len(practices_to_email)} practices")
        
        practices_to_update = []
        
        for practice in practices_to_email:
            # Check daily limit
            if not force_send and self.emails_sent_today >= self.daily_limit:
                logger.warning(f"Daily limit reached ({self.daily_limit}). Stopping campaign.")
                results['skipped_count'] = len(practices_to_email) - (results['success_count'] + results['failed_count'])
                break
            
            # Rate limiting
            self._enforce_rate_limit()
            
            # Process single practice
            success, result = self._process_single_practice(practice)
            
            results['results'].append(result)
            
            if success:
                results['success_count'] += 1
                self.emails_sent_today += 1
                practices_to_update.append(practice)
            else:
                results['failed_count'] += 1
        
        # Bulk update in DB
        if practices_to_update:
            self.db.bulk_upsert(practices_to_update)
            
        results['processing_time'] = round(time.time() - start_time, 2)
        
        logger.info(f"Campaign completed: {results['success_count']} sent, {results['failed_count']} failed, {results['skipped_count']} skipped")
        
        return results
    
    def _filter_practices_for_campaign(self, practices_data: List[Dict], today) -> List[Dict]:
        """Filter praktijken die vandaag een email moeten ontvangen"""
        filtered = []
        
        for practice in practices_data:
            if not practice.get('email'): continue
            if practice.get('status') == 'Klant': continue
            
            workflow = practice.get('workflow', {})
            if workflow.get('unsubscribed') or workflow.get('bounced'): continue
            
            emails_sent = workflow.get('emails_sent', 0)
            if emails_sent >= Config.MAX_EMAILS_PER_PRACTICE: continue
            
            next_followup = workflow.get('next_followup_date')
            if next_followup:
                followup_date = datetime.fromisoformat(next_followup).date()
                if today < followup_date: continue
            
            filtered.append(practice)
        
        return filtered
    
    def _process_single_practice(self, practice: Dict) -> Tuple[bool, Dict]:
        """Verwerk een enkele praktijk"""
        try:
            workflow = practice.get('workflow', {})
            emails_sent = workflow.get('emails_sent', 0)
            
            # Bepaal template
            template_name, delay = EmailTemplates.get_next_template(
                practice.get('status'),
                emails_sent,
                workflow.get('last_reply_date')
            )
            
            if not template_name:
                return False, {'status': 'skipped', 'reason': 'No template'}
            
            # Genereer email content
            if Config.OPENAI_API_KEY and emails_sent == 0:
                email_content = AIEmailGenerator.generate_personalized_email(practice, template_name)
            else:
                email_content = EmailTemplates.get_template(template_name, practice)
            
            # Verstuur email
            success, response = self.email_service.send_email(
                to_email=practice['email'],
                subject=email_content['subject'],
                body_text=email_content['body'],
                body_html=email_content.get('html'),
                custom_args={'practice_id': practice['nr']}
            )
            
            # Update workflow
            if success:
                self._update_practice_workflow(practice, template_name, delay, email_content)
                return True, {
                    'practice_id': practice['nr'],
                    'status': 'sent',
                    'template': template_name
                }
            else:
                return False, {'status': 'failed', 'error': response.get('error')}
        
        except Exception as e:
            logger.error(f"Error processing practice {practice.get('naam')}: {e}")
            return False, {'status': 'error', 'error': str(e)}
            
    def _update_practice_workflow(self, practice, template_name, delay, email_content):
        if 'workflow' not in practice: practice['workflow'] = {}
        now = datetime.now()
        
        practice['workflow'].update({
            'last_contact': now.isoformat(),
            'emails_sent': practice['workflow'].get('emails_sent', 0) + 1,
            'last_email_date': now.isoformat(),
            'last_email_template': template_name,
            'next_followup_date': (now.date() + delay).isoformat() if delay else None
        })
        
        if practice.get('status') == 'Nog niet benaderd':
            practice['status'] = 'Benaderd'

    def _enforce_rate_limit(self):
        if self.last_send_time:
            time_since_last = time.time() - self.last_send_time
            min_interval = 60 / self.rate_limit
            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)
        self.last_send_time = time.time()
