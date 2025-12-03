"""Database service - handles data persistence"""
import json
import os
import logging
from typing import List, Dict, Optional

from backend.config import Config

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service with Supabase and JSON fallback"""
    
    def __init__(self):
        self.data_file = Config.DATA_FILE
        self.supabase_client = self._init_supabase()
    
    def _init_supabase(self):
        """Initialize Supabase client if credentials available"""
        try:
            if Config.SUPABASE_URL and Config.SUPABASE_KEY:
                from supabase import create_client
                client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                logger.info("Supabase client initialized")
                return client
        except Exception as e:
            logger.warning(f"Supabase init failed: {e}")
        return None
    
    def get_practices(self) -> List[Dict]:
        """Get all practices"""
        if self.supabase_client:
            try:
                response = self.supabase_client.table('practices').select("*").execute()
                return response.data
            except Exception as e:
                logger.error(f"Supabase fetch error: {e}")
        
        # Fallback to JSON
        return self._load_from_json()
    
    def get_practice(self, practice_id: int) -> Optional[Dict]:
        """Get specific practice"""
        if self.supabase_client:
            try:
                response = self.supabase_client.table('practices').select("*").eq('nr', practice_id).execute()
                if response.data:
                    return response.data[0]
            except Exception as e:
                logger.error(f"Supabase fetch error: {e}")
        
        # Fallback to JSON
        practices = self._load_from_json()
        for practice in practices:
            if practice.get('nr') == practice_id:
                return practice
        return None
    
    def upsert_practice(self, practice: Dict) -> bool:
        """Insert or update practice"""
        if self.supabase_client:
            try:
                self.supabase_client.table('practices').upsert(practice).execute()
                return True
            except Exception as e:
                logger.error(f"Supabase upsert error: {e}")
        
        # Fallback to JSON
        return self._save_to_json_single(practice)
    
    def bulk_upsert(self, practices: List[Dict]) -> bool:
        """Bulk insert/update practices"""
        if self.supabase_client:
            try:
                self.supabase_client.table('practices').upsert(practices).execute()
                return True
            except Exception as e:
                logger.error(f"Supabase bulk error: {e}")
        
        # Fallback to JSON
        return self._save_to_json_bulk(practices)
    
    def _load_from_json(self) -> List[Dict]:
        """Load practices from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_to_json_single(self, practice: Dict) -> bool:
        """Save single practice to JSON"""
        try:
            practices = self._load_from_json()
            found = False
            
            for i, p in enumerate(practices):
                if p.get('nr') == practice.get('nr'):
                    practices[i] = practice
                    found = True
                    break
            
            if not found:
                practices.append(practice)
            
            with open(self.data_file, 'w') as f:
                json.dump(practices, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"JSON save error: {e}")
            return False
    
    def _save_to_json_bulk(self, new_practices: List[Dict]) -> bool:
        """Bulk save to JSON"""
        try:
            existing = self._load_from_json()
            existing_ids = {p.get('nr') for p in existing}
            
            for practice in new_practices:
                practice_id = practice.get('nr')
                if practice_id in existing_ids:
                    for i, p in enumerate(existing):
                        if p.get('nr') == practice_id:
                            existing[i] = practice
                            break
                else:
                    existing.append(practice)
            
            with open(self.data_file, 'w') as f:
                json.dump(existing, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"JSON bulk save error: {e}")
            return False
    
    def delete_practice(self, practice_id: int) -> bool:
        """Delete a practice"""
        if self.supabase_client:
            try:
                self.supabase_client.table('practices').delete().eq('nr', practice_id).execute()
                logger.info(f"Deleted practice {practice_id} from Supabase")
                return True
            except Exception as e:
                logger.error(f"Supabase delete error: {e}")
        
        # Fallback to JSON
        try:
            practices = self._load_from_json()
            original_count = len(practices)
            practices = [p for p in practices if p.get('nr') != practice_id]
            
            if len(practices) < original_count:
                with open(self.data_file, 'w') as f:
                    json.dump(practices, f, indent=2)
                logger.info(f"Deleted practice {practice_id} from JSON")
                return True
            else:
                logger.warning(f"Practice {practice_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"JSON delete error: {e}")
            return False
