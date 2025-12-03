# modules/ai_email_generator.py
import openai
from config import Config
import logging
import json

logger = logging.getLogger(__name__)
openai.api_key = Config.OPENAI_API_KEY

class AIEmailGenerator:
    """
    Gebruikt ChatGPT om ultra-gepersonaliseerde emails te genereren
    """
    
    @staticmethod
    def generate_personalized_email(praktijk_data, template_type='initial_outreach', 
                                    tone='professional_friendly'):
        """
        Genereert een volledig gepersonaliseerde email via ChatGPT
        """
        if not Config.OPENAI_API_KEY:
             logger.warning("OpenAI API Key missing. Returning template fallback.")
             from modules.email_templates import EmailTemplates
             return EmailTemplates.get_template(template_type, praktijk_data)

        # Bouw context prompt
        context = AIEmailGenerator._build_context_prompt(praktijk_data, template_type, tone)
        
        try:
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """Je bent een expert B2B sales copywriter gespecialiseerd in de gezondheidszorg. 
                        Je schrijft emails die:
                        - Professioneel maar toegankelijk zijn
                        - Focus op concrete voordelen (tijd, geld, tevredenheid)
                        - Geen buzzwords of marketing jargon gebruiken
                        - Kort en bondig zijn (max 150 woorden)
                        - Een duidelijke call-to-action hebben
                        - Respect tonen voor de drukke agenda van de ontvanger
                        
                        Schrijf in het Nederlands (België).
                        Return je antwoord als JSON met keys: subject, body, personalization_notes"""
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"AI email gegenereerd voor {praktijk_data.get('naam')}")
            
            return {
                'subject': result.get('subject', ''),
                'body': result.get('body', ''),
                'personalization_score': AIEmailGenerator._calculate_personalization_score(result),
                'personalization_notes': result.get('personalization_notes', ''),
                'ai_generated': True
            }
            
        except Exception as e:
            logger.error(f"AI generatie fout: {e}")
            # Fallback naar template
            from modules.email_templates import EmailTemplates
            return EmailTemplates.get_template(template_type, praktijk_data)
    
    @staticmethod
    def _build_context_prompt(praktijk_data, template_type, tone):
        """Bouwt de context prompt voor ChatGPT"""
        
        naam = praktijk_data.get('naam', 'de praktijk')
        gem = praktijk_data.get('gem', 'België')
        artsen = praktijk_data.get('artsen_namen', 'Onbekend')
        website = praktijk_data.get('website', 'Onbekend')
        emails_sent = praktijk_data.get('workflow', {}).get('emails_sent', 0)
        
        prompts = {
            'initial_outreach': f"""
Schrijf een introductie email voor:

**Praktijk:** {naam}
**Locatie:** {gem}
**Artsen:** {artsen}
**Website:** {website}

**Doel:** Introduceer ZorgCore, een AI-platform dat frontdesk taken automatiseert voor huisartsenpraktijken.

**Kernboodschap:**
- Automatiseer afspraakbeheer, patiëntcommunicatie, herhaalaanvragen
- Bespaart 15+ uur per week
- Kost €499/maand (vs €2000+ voor extra personeel)
- 30 dagen gratis trial

**Call-to-action:** Vraag voor 15 minuten demo call

**Toon:** {tone} - professioneel maar warm, respect voor hun tijd

**Let op:**
- Gebruik hun stadsnaam om lokale connectie te maken
- Als je artsen namen hebt, personaliseer de aanhef
- Geen overdreven marketing taal
- Focus op het probleem: te veel administratie, te weinig tijd voor patiënten
            """,
            
            'followup_1': f"""
Schrijf een korte follow-up email (5 dagen na eerste email):

**Praktijk:** {naam} in {gem}

**Situatie:** Ze hebben niet gereageerd op de eerste email.

**Doel:** Herinner hen vriendelijk aan het aanbod zonder pushy te zijn.

**Aanpak:**
- Erken dat ze het druk hebben
- Herhaal de grootste voordelen in 3 bullets
- Maak het super makkelijk om ja te zeggen (antwoord gewoon met JA)
- Bied ook optie om NEEN te zeggen (respectvol)

**Toon:** Begripvol, niet pushy, kortere email dan eerste keer
            """,
            
            'followup_2': f"""
Schrijf een laatste follow-up email (12 dagen na eerste email):

**Praktijk:** {naam}

**Situatie:** Dit is de laatste keer dat je contact opneemt.

**Doel:** Laatste kans aanbieding zonder desperate te klinken.

**Strategie:**
- Communiceer duidelijk: "dit is mijn laatste bericht"
- Bied extra incentive: 2 maanden gratis ipv 1
- Maak het urgent maar niet fake (early adopter deal)
- Geef hen ook de exit: "Geen interesse? Dan wens ik je veel succes"

**Toon:** Eerlijk, direct, respectvol afscheid mogelijk
            """
        }
        
        return prompts.get(template_type, prompts['initial_outreach'])
    
    @staticmethod
    def _calculate_personalization_score(email_content):
        """
        Bereken hoe gepersonaliseerd de email is (0-100)
        """
        score = 50  # Base score
        
        body = email_content.get('body', '').lower()
        
        # Check personalisatie elementen
        if any(name in body for name in ['dr.', 'dokter']):
            score += 10
        
        if len([word for word in body.split() if word[0].isupper()]) > 3:
            score += 10  # Proper names gebruikt
        
        if any(word in body for word in ['u', 'uw', 'jullie']):
            score += 10  # Direct aanspreekbaar
        
        if len(body.split()) < 200:
            score += 10  # Kort en bondig
        
        if '?' in body:
            score += 10  # Vraag gesteld (engagement)
        
        return min(score, 100)
    
    @staticmethod
    def improve_email_based_on_feedback(original_email, feedback, praktijk_data):
        """
        Verbeter een email based on feedback/resultaten
        """
        if not Config.OPENAI_API_KEY:
            return None

        try:
            prompt = f"""
Je bent een email optimization expert.

**Originele email:**
{original_email}

**Probleem:**
{feedback}

**Praktijk context:**
- Naam: {praktijk_data.get('naam')}
- Locatie: {praktijk_data.get('gem')}

**Opdracht:**
Herschrijf deze email om beter te presteren. Focus op:
- Sterkere subject line (als open rate laag is)
- Duidelijkere call-to-action (als respons rate laag is)
- Meer personalisatie
- Kortere, impactvolle tekst

Return als JSON met: improved_subject, improved_body, changes_made
            """
            
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Je bent een email optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Email improvement fout: {e}")
            return None
    
    @staticmethod
    def generate_subject_variations(base_subject, count=5):
        """
        Genereer meerdere subject line varianten voor A/B testing
        """
        if not Config.OPENAI_API_KEY:
            return [base_subject]

        try:
            prompt = f"""
Genereer {count} verschillende subject line varianten voor deze email:

**Basis subject:** {base_subject}

**Vereisten:**
- Elk verschillend in aanpak (vraag, statement, curiosity, urgency, value)
- Maximaal 60 karakters
- Nederlands (België)
- Geen clickbait

Return als JSON array: ["variant1", "variant2", ...]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )
            
            variants = json.loads(response.choices[0].message.content)
            return variants
            
        except Exception as e:
            logger.error(f"Subject generatie fout: {e}")
            return [base_subject]

# Batch AI Generation
class BatchAIGenerator:
    """
    Genereer emails voor meerdere praktijken tegelijk (efficiënter)
    """
    
    @staticmethod
    def generate_batch(practices_list, template_type='initial_outreach'):
        """
        Genereer emails voor lijst van praktijken in één API call
        """
        results = []
        
        # Split in batches van 10 (API limiet)
        batch_size = 10
        for i in range(0, len(practices_list), batch_size):
            batch = practices_list[i:i+batch_size]
            
            for practice in batch:
                try:
                    email = AIEmailGenerator.generate_personalized_email(
                        practice, 
                        template_type
                    )
                    results.append({
                        'practice_id': practice['nr'],
                        'email': email,
                        'success': True
                    })
                except Exception as e:
                    logger.error(f"Batch generatie fout voor {practice.get('naam')}: {e}")
                    results.append({
                        'practice_id': practice['nr'],
                        'error': str(e),
                        'success': False
                    })
        
        return results
