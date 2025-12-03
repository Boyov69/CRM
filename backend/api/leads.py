"""Lead generation API endpoints"""
from flask import Blueprint, jsonify, request
import logging

from backend.services.scraper import ScraperService

leads_bp = Blueprint('leads', __name__)
logger = logging.getLogger(__name__)

scraper = ScraperService()


@leads_bp.route('/leads/search', methods=['POST'])
def find_leads():
    """Search for leads by municipality"""
    gemeente = request.json.get('gemeente')
    
    if not gemeente:
        return jsonify({"error": "Gemeente verplicht"}), 400
    
    try:
        leads = scraper.search_leads(gemeente)
        return jsonify(leads)
    except Exception as e:
        logger.error(f"Lead search error: {e}")
        return jsonify({"error": str(e)}), 500


@leads_bp.route('/leads/scrape', methods=['POST'])
def scrape_practice():
    """Scrape details for specific practice"""
    naam = request.json.get('naam')
    gemeente = request.json.get('gemeente')
    
    if not naam or not gemeente:
        return jsonify({"error": "Naam en Gemeente verplicht"}), 400
    
    try:
        details = scraper.get_practice_details(naam, gemeente)
        return jsonify(details)
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return jsonify({"error": str(e)}), 500
