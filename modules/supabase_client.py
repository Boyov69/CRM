# modules/supabase_client.py
from supabase import create_client, Client
from config import Config
import logging

logger = logging.getLogger(__name__)

class SupabaseDB:
    """
    Wrapper voor Supabase interacties
    """
    
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_KEY
        self.client: Client = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        else:
            logger.warning("Supabase credentials missing")

    def get_practices(self):
        """Haal alle practices op"""
        if not self.client: return []
        
        try:
            response = self.client.table('practices').select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Supabase fetch error: {e}")
            return []

    def get_practice(self, practice_id):
        """Haal specifieke practice op"""
        if not self.client: return None
        
        try:
            response = self.client.table('practices').select("*").eq('nr', practice_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Supabase fetch error: {e}")
            return None

    def upsert_practice(self, practice_data):
        """Update of maak practice aan"""
        if not self.client: return False
        
        try:
            self.client.table('practices').upsert(practice_data).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase upsert error: {e}")
            return False
            
    def delete_practice(self, practice_id):
        """Verwijder practice"""
        if not self.client: return False
        
        try:
            self.client.table('practices').delete().eq('nr', practice_id).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase delete error: {e}")
            return False

    def bulk_upsert(self, practices_list):
        """Bulk update/insert"""
        if not self.client: return False
        
        try:
            # Supabase upsert supports lists
            self.client.table('practices').upsert(practices_list).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase bulk error: {e}")
            return False
