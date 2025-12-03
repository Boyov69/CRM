# modules/email_templates.py
from datetime import datetime, timedelta
import random

class EmailTemplates:
    """
    Geavanceerd template systeem met A/B testing en personalisatie
    """
    
    # Emoji sets voor verschillende tones
    PROFESSIONAL_EMOJIS = ['✅', '📊', '💼', '🎯', '⚡']
    FRIENDLY_EMOJIS = ['😊', '👋', '🌟', '💡', '🚀']
    
    @staticmethod
    def get_subject_variants(praktijk_data, template_type):
        """
        Genereert meerdere subject line varianten voor A/B testing
        """
        naam = praktijk_data.get('naam', 'uw praktijk')
        gem = praktijk_data.get('gem', 'uw regio')
        
        subjects = {
            'initial_outreach': [
                f"💡 Automatiseer {naam} met AI - Gratis demo",
                f"Speciale aanbieding voor huisartsen in {gem}",
                f"⚡ {naam}: 15 uur/week tijdwinst mogelijk?",
                f"Exclusief voor praktijken in {gem}: AI assistentie",
                f"🎯 80% minder administratie bij {naam} - hoe?"
            ],
            'followup_1': [
                f"Re: Vraag over {naam} - nog interesse?",
                f"Quick question voor {naam}",
                f"⏰ 10 minuten voor een productiviteitsboost?",
                f"Korte follow-up: AI voor {naam}",
                f"Laatste kans gratis demo voor {gem}"
            ],
            'followup_2': [
                f"🎁 Exclusieve aanbieding voor {naam} (laatste reminder)",
                f"Afsluitend bericht voor {naam}",
                f"Gratis maand - alleen voor early adopters in {gem}",
                f"Final call: Automatisering voor {naam}",
                f"Ik geef het op 😊 (maar eerst dit...)"
            ],
            'demo_booked': [
                f"✅ Bevestiging: Demo voor {naam}",
                f"Klaar voor uw demo - {naam}",
                f"📅 Afspraak bevestigd: {naam}"
            ]
        }
        
        return random.choice(subjects.get(template_type, subjects['initial_outreach']))
    
    @staticmethod
    def get_template(template_name, praktijk_data, personalization_level='medium'):
        """
        Genereert gepersonaliseerde email templates
        
        Args:
            template_name: Type template (initial_outreach, followup_1, etc.)
            praktijk_data: Dictionary met praktijk informatie
            personalization_level: 'low', 'medium', 'high'
        """
        naam = praktijk_data.get('naam', 'Geachte praktijk')
        gem = praktijk_data.get('gem', 'uw regio')
        artsen = praktijk_data.get('artsen_namen', '')
        
        # Personalisatie elementen
        greeting = EmailTemplates._get_greeting(naam, artsen, personalization_level)
        local_touch = EmailTemplates._get_local_touch(gem, personalization_level)
        signature = EmailTemplates._get_signature()
        
        templates = {
            "initial_outreach": {
                "subject": EmailTemplates.get_subject_variants(praktijk_data, 'initial_outreach'),
                "body": f"""
{greeting}

Ik ben Tom van ZorgCore, en we helpen huisartsenpraktijken in België om hun frontdesk volledig te automatiseren met AI-technologie.

{local_touch}

**Waarom dit e-mailtje?**

Onze AI-assistent neemt deze taken over:
✅ Afspraakbeheer (telefoon + online)
✅ Herhaalaanvragen medicatie
✅ Patiëntencommunicatie 24/7
✅ Administratieve follow-ups

**Praktijkvoorbeeld:**
Huisartsenpraktijk in Hasselt bespaart sinds 3 maanden:
• 18 uur/week aan telefoonwerk
• €2.400/maand aan personeelskosten
• 95% patiënttevredenheid

**Speciale lanceringsaanbieding:**
🎁 30 dagen gratis proberen
🎁 Persoonlijke demo op uw praktijk
🎁 Geen installatiekosten

Heeft u 15 minuten deze week voor een korte video-demo?
Antwoord gewoon met "JA" en ik stuur u direct de beschikbare momenten.

{signature}

PS: Ik begrijp dat u het druk heeft. Daarom: als u nu niet geïnteresseerd bent, laat het me weten en u hoort niets meer van mij!
                """,
                "html": EmailTemplates._generate_html_template(
                    greeting, naam, gem, template_name
                )
            },
            
            "followup_1": {
                "subject": EmailTemplates.get_subject_variants(praktijk_data, 'followup_1'),
                "body": f"""
{greeting}

Ik stuurde u vorige week een bericht over onze AI-oplossing voor automatisering van frontdesk taken.

Ik snap dat u overspoeld wordt met e-mails, dus houd ik het kort:

**3 redenen waarom praktijken in {gem} al zijn overgestapt:**

1. ⏰ **Tijd:** Gemiddeld 15+ uur per week tijdwinst
2. 💰 **Geld:** €2.000+ besparing per maand (vs. extra personeel)
3. 😊 **Tevredenheid:** Patiënten kunnen 24/7 terecht

**Nieuw: Nu ook integratie met Medispring/Topaz**

Zullen we volgende week 10 minuten bellen?  
U kiest de dag en het tijdstip. Antwoord met uw voorkeur of klik hier: [CALENDLY LINK]

{signature}

PS: Niet geïnteresseerd? Antwoord met "NEE BEDANKT" en ik verwijder u uit mijn lijst. Geen hard feelings! 😊
                """,
                "html": EmailTemplates._generate_html_template(
                    greeting, naam, gem, template_name
                )
            },
            
            "followup_2": {
                "subject": EmailTemplates.get_subject_variants(praktijk_data, 'followup_2'),
                "body": f"""
{greeting}

Dit is mijn laatste bericht - belooft! 😊

Ik wil u niet blijven lastigvallen, maar voordat ik u uit mijn lijst haal, wilde ik deze exclusieve aanbieding delen:

**🎁 Last Chance Aanbieding (alleen deze week):**

Als u zich deze week nog aanmeldt, krijgt u:
✅ 2 maanden gratis (waarde €998)
✅ Gratis onboarding en training (waarde €500)
✅ Priority support (eerste 3 maanden)
✅ Gratis integratie met uw huidige systeem

**Totale waarde: €1.498 - nu gratis voor early adopters**

**Geen verplichtingen:**
- Annuleer wanneer u wilt
- Geen contract
- Setup in 48 uur

Interesse? Antwoord gewoon **"JA"** en ik regel alles.

Geen interesse? Geen probleem! Dan wens ik u veel succes en een fijne dag verder.

{signature}

PS: Dit aanbod geldt tot vrijdag 23:59. Daarna zijn we uitverkocht voor Q1.
                """,
                "html": EmailTemplates._generate_html_template(
                    greeting, naam, gem, template_name
                )
            },
            
            "demo_booked": {
                "subject": EmailTemplates.get_subject_variants(praktijk_data, 'demo_booked'),
                "body": f"""
{greeting}

Super! Bedankt voor uw interesse in ZorgCore. 🎉

**📅 Demo Details:**

Datum: [DATUM]
Tijdstip: [TIJD]
Duur: 20 minuten
Type: Online via Google Meet

**🔗 Meeting Link:**
[GOOGLE MEET LINK]

**Wat u kunt verwachten:**
✅ Live demonstratie van het AI-platform
✅ Antwoorden op al uw vragen
✅ Gepersonaliseerd implementatieplan voor {naam}
✅ Exclusieve early adopter voorwaarden

**Voor de demo:**
Geen voorbereiding nodig! Maar als u specifieke vragen heeft, stuur ze gerust alvast door.

**Moet u de afspraak verzetten?**
Geen probleem, antwoord op deze e-mail of klik hier: [RESCHEDULE LINK]

Ik kijk ernaar uit om u te spreken!

{signature}

PS: Demo kan niet doorgaan? Laat het me weten, dan vinden we een beter moment.
                """,
                "html": EmailTemplates._generate_html_template(
                    greeting, naam, gem, template_name
                )
            },
            
            "re_engagement": {
                "subject": f"🤔 Mis ik iets? - {naam}",
                "body": f"""
{greeting}

Ik heb u een paar weken geleden gecontacteerd over automatisering van uw frontdesk.

Eerlijk: ik weet niet of mijn berichten u bereikt hebben, of dat u gewoon (terecht) geen interesse heeft.

**Mag ik één vraag stellen?**

Is dit niet interessant omdat:
a) Te duur
b) Geen tijd om dit te bekijken
c) Al een oplossing gevonden
d) Iets anders

Antwoord gerust eerlijk! Dit helpt mij enorm om andere praktijken beter te helpen.

En als dit gewoon niet relevant is, zeg het gerust - dan stop ik met e-mailen. 😊

{signature}
                """
            },
            
            "client_onboarding": {
                "subject": f"🎉 Welkom bij ZorgCore, {naam}!",
                "body": f"""
{greeting}

Welkom aan boord! 🚀

We zijn blij dat {naam} kiest voor ZorgCore. Dit wordt het begin van meer tijd en minder stress.

**📋 Volgende stappen:**

**Week 1: Setup**
- Maandag: Kickoff call (30 min)
- Woensdag: Systeem configuratie
- Vrijdag: Eerste test run

**Week 2: Training**
- Maandag: Team training (1 uur)
- Woensdag: Q&A sessie
- Vrijdag: Go-live!

**Week 3-4: Optimalisatie**
- Dagelijkse monitoring
- Fine-tuning AI
- Feedback sessies

**🆘 Support:**
- Telefoon: [NUMMER]
- Email: support@zorgcore.be
- Chat: 24/7 beschikbaar in uw dashboard

**📚 Bronnen:**
- Handleiding: [LINK]
- Video tutorials: [LINK]
- FAQ: [LINK]

Uw persoonlijke onboarding specialist is [NAAM].
Ze neemt morgen contact met u op.

Vragen? Bel of mail gerust!

{signature}

PS: Welkomstcadeau komt deze week aan 🎁
                """
            }
        }
        
        template = templates.get(template_name, templates["initial_outreach"])
        
        # Return both plain text and HTML
        return {
            "subject": template["subject"],
            "body": template["body"],
            "html": template.get("html", EmailTemplates._text_to_html(template["body"]))
        }
    
    @staticmethod
    def _get_greeting(naam, artsen, level):
        """Genereert gepersonaliseerde begroeting"""
        if level == 'high' and artsen:
            doctors_list = artsen.split(',')
            if len(doctors_list) == 1:
                return f"Dag Dr. {doctors_list[0].strip()},"
            else:
                return f"Dag team van {naam},"
        elif level == 'medium':
            return f"Beste team van {naam},"
        else:
            return "Geachte heer/mevrouw,"
    
    @staticmethod
    def _get_local_touch(gemeente, level):
        """Voegt lokale context toe"""
        local_touches = {
            'Hasselt': "We werken al samen met meerdere praktijken in Hasselt en omgeving.",
            'Genk': "Praktijken in Genk zien gemiddeld 20% meer efficiëntie na implementatie.",
            'Tongeren': "U bent de vierde praktijk in Tongeren die we contacteren - er is duidelijk vraag naar automatisering in uw regio!",
        }
        
        if level == 'high' and gemeente in local_touches:
            return local_touches[gemeente]
        elif level == 'medium':
            return f"We zien veel interesse van praktijken in {gemeente}."
        else:
            return ""
    
    @staticmethod
    def _get_signature():
        """Standaard handtekening"""
        return """
Met vriendelijke groet,

Tom Claessens
Oprichter, ZorgCore

📞 +32 11 123 456
📧 tom@zorgcore.be
🌐 www.zorgcore.be
LinkedIn: linkedin.com/in/tomclaessens
        """.strip()
    
    @staticmethod
    def _text_to_html(text):
        """Converteert plain text naar basis HTML"""
        html = text.replace('\n', '<br>')
        # Bold text
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        return f"<div style='font-family: Arial, sans-serif; line-height: 1.6;'>{html}</div>"
    
    @staticmethod
    def _generate_html_template(greeting, naam, gemeente, template_type):
        """
        Genereert professionele HTML email template
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZorgCore</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: 'Segoe UI', Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <!-- Main Container -->
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #00ff9d 0%, #00d4ff 100%); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #000000; font-size: 28px; font-weight: 700;">
                                ZorgCore
                            </h1>
                            <p style="margin: 5px 0 0 0; color: #000000; font-size: 14px; opacity: 0.8;">
                                AI voor Huisartsenpraktijken
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="font-size: 16px; color: #333; line-height: 1.6; margin: 0 0 20px 0;">
                                {greeting}
                            </p>
                            
                            <!-- Dynamic content goes here -->
                            <div style="font-size: 15px; color: #555; line-height: 1.8;">
                                [MAIN_CONTENT]
                            </div>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="[CTA_LINK]" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #00ff9d 0%, #00d4ff 100%); color: #000000; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(0,255,157,0.3);">
                                            📅 Plan Gratis Demo
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Signature -->
                            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                                <p style="font-size: 15px; color: #333; margin: 0 0 5px 0;">
                                    Met vriendelijke groet,
                                </p>
                                <p style="font-size: 16px; color: #000; font-weight: 600; margin: 0 0 10px 0;">
                                    Tom Claessens
                                </p>
                                <p style="font-size: 13px; color: #666; margin: 0; line-height: 1.6;">
                                    Oprichter, ZorgCore<br>
                                    📞 +32 11 123 456<br>
                                    📧 tom@zorgcore.be
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f8f8; padding: 20px 30px; border-top: 1px solid #e0e0e0;">
                            <p style="font-size: 12px; color: #888; margin: 0 0 10px 0; line-height: 1.5;">
                                U ontvangt deze email omdat u een huisartsenpraktijk runt in België.
                            </p>
                            <p style="font-size: 12px; color: #888; margin: 0;">
                                <a href="[UNSUBSCRIBE_LINK]" style="color: #00ff9d; text-decoration: none;">Uitschrijven</a> | 
                                <a href="[PREFERENCES_LINK]" style="color: #00ff9d; text-decoration: none;">Voorkeuren</a> |
                                <a href="https://www.zorgcore.be" style="color: #00ff9d; text-decoration: none;">Website</a>
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
    
    <!-- Tracking Pixel -->
    <img src="[TRACKING_PIXEL_URL]" width="1" height="1" alt="" />
</body>
</html>
        """
    
    @staticmethod
    def get_next_template(current_status, emails_sent, last_reply_date=None):
        """
        Bepaalt welke template als volgende moet worden verstuurd
        
        Returns:
            (template_name, delay_days)
        """
        # Als klant heeft gereageerd
        if last_reply_date:
            return "demo_booked", timedelta(days=0)
        
        # Standaard flow
        if emails_sent == 0:
            return "initial_outreach", timedelta(days=0)
        elif emails_sent == 1:
            return "followup_1", timedelta(days=5)
        elif emails_sent == 2:
            return "followup_2", timedelta(days=7)
        elif emails_sent >= 3 and emails_sent < 5:
            # Re-engagement na 30 dagen
            return "re_engagement", timedelta(days=30)
        else:
            return None, None

# A/B Testing Support
class ABTestingManager:
    """Beheert A/B tests voor subject lines en content"""
    
    @staticmethod
    def select_variant(praktijk_id, template_type):
        """
        Selecteert een variant voor A/B testing
        Gebruikt praktijk_id als seed voor consistentie
        """
        random.seed(praktijk_id)
        variant = random.choice(['A', 'B', 'C'])
        random.seed()  # Reset seed
        return variant
    
    @staticmethod
    def track_variant_performance(variant, metric, value):
        """Track welke variant beter presteert"""
        # Implementeer analytics tracking
        pass
