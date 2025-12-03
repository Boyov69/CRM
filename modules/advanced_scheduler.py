# modules/advanced_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta
import pytz
import logging
from config import Config

logger = logging.getLogger(__name__)

class AdvancedScheduler:
    """Advanced job scheduler voor CRM automation"""
    
    def __init__(self, timezone: str = 'Europe/Brussels'):
        self.timezone = pytz.timezone(timezone)
        
        # Use SQLAlchemyJobStore if DB URL is configured, else Memory
        if Config.DATABASE_URL and 'postgresql' in Config.DATABASE_URL:
            jobstores = {'default': SQLAlchemyJobStore(url=Config.DATABASE_URL)}
        else:
            jobstores = None # Default to MemoryJobStore
            
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            timezone=self.timezone
        )
        logger.info(f"Scheduler initialized with timezone: {timezone}")
    
    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
            
    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            
    def schedule_daily_campaign(self, hour=9, minute=0):
        """Schedule daily campaign run"""
        self.scheduler.add_job(
            self._run_campaign_job,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=self.timezone),
            id='daily_campaign',
            replace_existing=True
        )
        logger.info(f"Scheduled daily campaign at {hour}:{minute:02d}")

    def schedule_response_check(self, interval_minutes=60):
        """Schedule response check"""
        self.scheduler.add_job(
            self._check_responses_job,
            trigger=IntervalTrigger(minutes=interval_minutes, timezone=self.timezone),
            id='response_check',
            replace_existing=True
        )
        logger.info(f"Scheduled response check every {interval_minutes} minutes")

    def _run_campaign_job(self):
        """Wrapper to run campaign"""
        from app import start_campaign_internal
        logger.info("Running scheduled campaign...")
        start_campaign_internal()

    def _check_responses_job(self):
        """Wrapper to check responses"""
        from modules.response_tracker import GmailResponseTracker
        # Implementation depends on how we want to trigger this
        pass
