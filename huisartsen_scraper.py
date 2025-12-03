import csv
import re
import time
import requests
from bs4 import BeautifulSoup
from googlesearch import search  # Vereist: pip install googlesearch-python

# --- CONFIGURATIE ---
# Pas dit aan naar uw bestandsnaam. 
# Het CSV bestand moet kolommen hebben: 'Naam', 'Gemeente'
INPUT_BESTAND = 'huisartsen_lijst_limburg.csv' 
OUTPUT_BESTAND = 'huisartsen_met_emails.csv'

def find_email_in_text(text):
    # Regex om email adressen te vinden
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    # Filter 'vuile' emails eruit (zoals png@..., example@...)
    clean_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', 'wixpress.com'))]
    return list(set(clean_emails)) # Verwijder dubbels

def find_phone_in_text(text):
    # Regex voor Belgische nummers (vast en mobiel)
    phone_pattern = r'(?:\+32|0)[1-9](?:[\s\.-]*\d{2}){3,4}'
    phones = re.findall(phone_pattern, text)
    return list(set([p.strip() for p in phones]))

def search_duckduckgo(query):
    """Fallback zoekfunctie via DuckDuckGo HTML"""
    print(f"🦆 DuckDuckGo fallback voor: {query}")
    url = "https://html.duckduckgo.com/html/"
    data = {'q': query}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Eerste resultaat link
            first_link = soup.find('a', class_='result__a')
            if first_link:
                return first_link['href']
    except Exception as e:
        print(f"⚠️ DDG Fout: {e}")
    return None

def get_website_and_email(naam, gemeente):
    query = f"Huisarts {naam} {gemeente} website"
    print(f"🔍 Zoeken naar: {query}...")
    
    found_website = "Niet gevonden"
    found_emails = []
    found_phones = []
    found_riziv = []
    found_doctors = []

    try:
        # 1. Zoek de eerste URL via Google
        urls = []
        try:
            search_results = search(query, num_results=1, lang="nl")
            urls = list(search_results)
        except Exception as e:
            print(f"⚠️ Google Search Fout: {e}")

        if not urls:
            # Fallback naar DuckDuckGo
            ddg_url = search_duckduckgo(query)
            if ddg_url:
                urls = [ddg_url]
            else:
                return "Niet gevonden", "Geen email", "", "", ""

        found_website = urls[0]
        
        if "goudengids" in found_website or "open openingsuren" in found_website:
             return found_website, "Waarschijnlijk gids-site", "", "", ""

        # 2. Bezoek de website
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(found_website, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()
            
            # Emails zoeken
            found_emails.extend(find_email_in_text(text_content))
            for a in soup.find_all('a', href=True):
                if 'mailto:' in a['href']:
                    found_emails.append(a['href'].replace('mailto:', '').split('?')[0])

            # Telefoonnummers zoeken
            found_phones.extend(find_phone_in_text(text_content))

            # RIZIV nummers zoeken (1-00000-00-000 of varianten)
            riziv_pattern = r'\d-\d{5}-\d{2}-\d{3}'
            found_riziv.extend(re.findall(riziv_pattern, text_content))

            # Doktersnamen zoeken (Heuristiek: Dr. Naam Achternaam)
            doctor_pattern = r'Dr\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+'
            found_doctors.extend(re.findall(doctor_pattern, text_content))

            # Contact pagina check
            if not found_emails:
                for a in soup.find_all('a', href=True):
                    if 'contact' in a.text.lower() or 'contact' in a['href'].lower():
                        contact_url = a['href']
                        if not contact_url.startswith('http'):
                            contact_url = found_website.rstrip('/') + '/' + contact_url.lstrip('/')
                        try:
                            resp_contact = requests.get(contact_url, headers=headers, timeout=5)
                            contact_text = resp_contact.text
                            found_emails.extend(find_email_in_text(contact_text))
                            found_phones.extend(find_phone_in_text(contact_text))
                        except:
                            pass
                        break

    except Exception as e:
        print(f"❌ Fout bij {naam}: {e}")
        return found_website, "Error", "", "", ""

    # Opschonen
    email_string = "; ".join(list(set(found_emails))) if found_emails else "Geen email"
    phone_string = "; ".join(list(set(found_phones))) if found_phones else ""
    riziv_string = "; ".join(list(set(found_riziv))) if found_riziv else ""
    doctors_string = "; ".join(list(set(found_doctors))) if found_doctors else ""
    
    return found_website, email_string, phone_string, riziv_string, doctors_string

def search_leads(gemeente):
    """
    Zoekt naar huisartsen in een specifieke gemeente via Nominatim (OSM).
    """
    print(f"🌍 Zoeken naar leads in: {gemeente}")
    base_url = "https://nominatim.openstreetmap.org/search"
    
    # Zoek specifiek naar artsen/dokters
    params = {
        "q": f"doctors in {gemeente}",
        "format": "json",
        "addressdetails": 1,
        "extratags": 1, # Vraag extra tags op (website, phone, etc.)
        "limit": 50
    }
    
    headers = {
        'User-Agent': 'ZorgCoreCRM/1.0 (contact@zorgcore.be)' 
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        results = response.json()
        
        leads = []
        for item in results:
            name = item.get('name') or item.get('display_name').split(',')[0]
            
            # Adres opbouwen
            addr = item.get('address', {})
            street = addr.get('road', '')
            number = addr.get('house_number', '')
            postcode = addr.get('postcode', '')
            city = addr.get('city') or addr.get('town') or addr.get('village', gemeente)
            
            full_address = f"{street} {number}".strip()
            if postcode: full_address += f", {postcode}"
            if city: full_address += f" {city}"
            
            # Extra tags ophalen
            extras = item.get('extratags', {})
            phone = extras.get('contact:phone') or extras.get('phone') or ""
            website = extras.get('contact:website') or extras.get('website') or ""
            
            leads.append({
                "naam": name,
                "praktijk": name,
                "adres": full_address,
                "gem": city,
                "type": "Onbekend",
                "tel": phone,
                "website": website
            })
            
        return leads

    except Exception as e:
        print(f"❌ Fout bij zoeken leads: {e}")
        return []

# --- HOOFD PROGRAMMA ---
def main():
    # Lees de input CSV
    # Zorg dat u een bestand 'huisartsen_lijst_limburg.csv' heeft met headers 'Naam' en 'Gemeente'
    # Voorbeeld data om te testen als er geen bestand is:
    test_data = [
        {"Naam": "Praktijk De Rode Rok", "Gemeente": "Hasselt"},
        {"Naam": "Huisartsen De Statie", "Gemeente": "Zonhoven"},
        # ... voeg hier uw 820 rijen toe ...
    ]

    print("🚀 Start Huisartsen Scraper Limburg...")
    
    with open(OUTPUT_BESTAND, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Naam', 'Gemeente', 'Gevonden Website', 'Gevonden Email'])

        # Vervang 'test_data' door uw CSV lezer logica als u het bestand heeft
        for row in test_data:
            website, email = get_website_and_email(row['Naam'], row['Gemeente'])
            print(f"   👉 Resultaat: {email}")
            writer.writerow([row['Naam'], row['Gemeente'], website, email])
            
            # Wacht even om Google niet boos te maken (Anti-bot)
            time.sleep(2)

    print(f"✅ Klaar! Data opgeslagen in {OUTPUT_BESTAND}")

if __name__ == "__main__":
    main()
