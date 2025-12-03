from modules.response_tracker import GmailResponseTracker
import os

def setup_gmail():
    print("=== Gmail API Setup ===")
    print("Zorg ervoor dat je 'credentials.json' hebt gedownload van Google Cloud Console")
    print("en in deze map hebt geplaatst.")
    print("---------------------------------------------------")
    
    if not os.path.exists('credentials.json'):
        print("❌ FOUT: 'credentials.json' niet gevonden!")
        print("Download deze via: https://console.cloud.google.com/apis/credentials")
        return

    print("Start authenticatie proces...")
    try:
        tracker = GmailResponseTracker()
        if tracker.service:
            print("✅ Succes! 'token.json' is aangemaakt.")
            print("Je kunt nu de Gmail integratie gebruiken.")
        else:
            print("❌ Authenticatie mislukt.")
    except Exception as e:
        print(f"❌ Er ging iets mis: {e}")

if __name__ == "__main__":
    setup_gmail()
