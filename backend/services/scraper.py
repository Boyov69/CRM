"""Web scraping service"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class ScraperService:
    """Web scraping service for healthcare practices"""
    
    def search_leads(self, gemeente: str) -> List[Dict]:
        """Search for leads in municipality"""
        try:
            from huisartsen_scraper import search_leads
            return search_leads(gemeente)
        except Exception as e:
            logger.error(f"Lead search error: {e}")
            return []
    
    def get_practice_details(self, naam: str, gemeente: str) -> Dict:
        """Get detailed practice information"""
        try:
            from huisartsen_scraper import get_website_and_email
            website, email, phone, riziv, doctors = get_website_and_email(naam, gemeente)
            
            return {
                "website": website,
                "email": email,
                "tel": phone,
                "riziv": riziv,
                "artsen": doctors
            }
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return {}
