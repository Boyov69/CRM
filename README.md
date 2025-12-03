# 🏥 Huisartsen CRM & Data Scraper

Een geavanceerd CRM-systeem voor het beheren van huisartsenpraktijken in België, inclusief geautomatiseerde data scraping, intelligente email campagnes, en AI-gedreven communicatie.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Inhoudsopgave

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installatie](#-installatie)
- [Configuratie](#-configuratie)
- [Gebruik](#-gebruik)
- [Project Structuur](#-project-structuur)
- [API Endpoints](#-api-endpoints)
- [Modules](#-modules)
- [Database Schema](#-database-schema)
- [Development](#-development)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔍 Data Scraping
- Automatisch verzamelen van praktijkgegevens van publieke websites
- Ophalen van contactinformatie (email, telefoon, website)
- RIZIV nummer extractie
- Artseninformatie scraping
- Gemeente-gebaseerde lead discovery

### 📧 Email Automatisering
- Multi-provider support (SendGrid, Gmail API, SMTP)
- Template-based email system
- Drip campaigns met geautomatiseerde follow-ups
- Rate limiting en daily email caps
- Open & click tracking
- Response detection via Gmail API

### 🤖 AI Integratie
- GPT-4 powered email personalisatie
- Context-aware content generatie
- Template customization per praktijk
- Natuurlijke taalverwerking voor betere engagement

### 💾 Database Management
- Supabase cloud database integratie
- Real-time data synchronisatie
- Fallback naar local JSON storage
- Bulk operations support
- Practice workflow tracking

### 📊 Analytics & Reporting
- Real-time campagne statistieken
- Conversion funnel analyse
- ROI projecties
- Email performance metrics
- Response rate tracking

### 🔔 Notificaties
- Slack webhook integratie
- Real-time campagne updates
- Response alerts
- Error notifications

### 🎯 Workflow Management
- Multi-stage email sequences
- Status tracking (Nieuw → Contacted → Lead → Client)
- Automated next actions
- Follow-up scheduling

---

## 🛠 Tech Stack

### Backend
- **Flask** - Web framework
- **Python 3.8+** - Core language
- **Supabase** - PostgreSQL database
- **OpenAI GPT-4** - AI email generation
- **SendGrid** - Email delivery
- **Gmail API** - Response tracking

### Frontend
- **HTML5/CSS3** - UI
- **JavaScript** - Interactivity
- **Bootstrap** - Responsive design

### Infrastructure
- **Gunicorn** - WSGI server
- **APScheduler** - Task scheduling
- **BeautifulSoup4** - Web scraping
- **python-dotenv** - Environment management

---

## 🚀 Installatie

### Prerequisites
- Python 3.8 of hoger
- pip (Python package manager)
- Git
- Supabase account (optioneel, maar aanbevolen)
- SendGrid account voor email verzending

### Stap 1: Clone de Repository
```bash
git clone https://github.com/Boyov69/CRM.git
cd CRM
```

### Stap 2: Virtual Environment (Aanbevolen)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Stap 3: Installeer Dependencies
```bash
pip install -r requirements.txt
```

### Stap 4: Environment Setup
Kopieer het `.env.example` bestand naar `.env`:
```bash
cp .env.example .env
```

---

## ⚙️ Configuratie

### Environment Variables

Bewerk `.env` en vul de volgende waarden in:

```env
# Flask
SECRET_KEY=jouw-super-geheime-sleutel-verander-dit
FLASK_DEBUG=False

# Email Provider (kies: sendgrid, gmail, smtp)
EMAIL_PROVIDER=sendgrid

# SendGrid (AANBEVOLEN voor productie)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@jouwebedrijf.be
SENDGRID_FROM_NAME=Jouw Bedrijfsnaam

# Gmail API (voor response tracking)
# Download credentials.json van Google Cloud Console
# Plaats in project root

# Supabase Database
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# OpenAI (voor AI-gegenereerde emails)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4

# Slack Notificaties (optioneel)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx

# Campaign Settings
MAX_EMAILS_PER_PRACTICE=3
DAILY_EMAIL_LIMIT=100
EMAILS_PER_MINUTE=10

# Tracking
ENABLE_OPEN_TRACKING=True
ENABLE_CLICK_TRACKING=True

# Logging
LOG_LEVEL=INFO
```

### Gmail API Setup (voor response tracking)
1. Ga naar [Google Cloud Console](https://console.cloud.google.com/)
2. Maak een nieuw project aan
3. Enable Gmail API
4. Download OAuth 2.0 credentials als `credentials.json`
5. Plaats in project root
6. Run eerste keer:
```bash
python setup_gmail.py
```

### Supabase Database Setup
1. Maak een gratis account op [supabase.com](https://supabase.com)
2. Maak een nieuw project aan
3. Kopieer URL en anon key naar `.env`
4. Run database migratie:
```bash
python scripts/migrate_to_supabase.py
```

---

## 🎯 Gebruik

### Start de Applicatie
```bash
python app.py
```
De applicatie draait op `http://localhost:5000`

### Dashboard
Open je browser en navigeer naar `http://localhost:5000` voor:
- Praktijkbeheer
- Campagne overzicht
- Analytics dashboard
- Lead scraping interface

### Campagnes Starten

#### Via Dashboard
1. Ga naar Campagnes tab
2. Selecteer praktijken
3. Kies email template
4. Enable AI generatie (optioneel)
5. Klik "Start Campagne"

#### Via Command Line
```bash
# Basic campagne
python run_campaign.py

# Met AI personalisatie
python run_campaign.py --ai

# Specifieke template
python run_campaign.py --template initial_outreach

# Custom API URL
python run_campaign.py --url http://localhost:5000
```

### Praktijken Scrapen
```bash
# Via dashboard
# Ga naar "Leads" tab en voer gemeente in

# Of gebruik de API:
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"gemeente":"Brussel"}'
```

---

## 📁 Project Structuur

```
CRM/
├── app.py                      # Hoofd Flask applicatie
├── config.py                   # Configuratie management
├── requirements.txt            # Python dependencies
├── run_campaign.py            # CLI campagne tool
├── huisartsen_scraper.py      # Data scraping logica
├── setup_gmail.py             # Gmail API setup helper
├── setup_git.sh               # Git initialisatie script
│
├── modules/                   # Core modules
│   ├── email_automation.py    # Email workflow engine
│   ├── email_templates.py     # Email template systeem
│   ├── sendgrid_integration.py # SendGrid service
│   ├── ai_email_generator.py  # OpenAI integratie
│   ├── response_tracker.py    # Gmail response detector
│   ├── supabase_client.py     # Database client
│   ├── analytics.py           # Analytics engine
│   ├── slack_notifications.py # Slack integratie
│   ├── advanced_scheduler.py  # Task scheduler
│   └── models.py              # Data models
│
├── scripts/                   # Utility scripts
│   └── migrate_to_supabase.py # Database migratie
│
├── templates/                 # HTML templates
│   └── index.html            # Dashboard UI
│
├── static/                    # Static assets
│   ├── css/                  # Stylesheets
│   └── js/                   # JavaScript files
│
├── data/                      # Data directory
│   └── practices.json        # Fallback JSON storage
│
├── logs/                      # Log files
│   └── campaign.log          # Application logs
│
└── .github/                   # GitHub workflows
    └── workflows/
        └── deploy.yml        # CI/CD pipeline
```

---

## 🔌 API Endpoints

### Practices Management

#### `GET /api/practices`
Haal alle praktijken op
```bash
curl http://localhost:5000/api/practices
```

#### `POST /api/practices`
Voeg nieuwe praktijk toe
```bash
curl -X POST http://localhost:5000/api/practices \
  -H "Content-Type: application/json" \
  -d '{
    "naam": "Praktijk De Zorg",
    "gemeente": "Antwerpen",
    "email": "info@dezorg.be",
    "tel": "03 123 45 67"
  }'
```

### Lead Generation

#### `POST /api/leads`
Zoek nieuwe leads in gemeente
```bash
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"gemeente": "Gent"}'
```

#### `POST /api/scrape`
Scrape details van specifieke praktijk
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"naam": "Praktijk X", "gemeente": "Brussel"}'
```

### Campaign Management

#### `POST /api/campaign/start`
Start email campagne
```bash
curl -X POST http://localhost:5000/api/campaign/start \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3],
    "template": "initial_outreach",
    "use_ai": true
  }'
```

#### `GET /api/campaign/stats`
Haal campagne statistieken op
```bash
curl http://localhost:5000/api/campaign/stats
```

#### `POST /api/practice/<id>/mark-replied`
Markeer praktijk als 'heeft gereageerd'
```bash
curl -X POST http://localhost:5000/api/practice/123/mark-replied
```

---

## 🧩 Modules

### Email Templates (`modules/email_templates.py`)
- Pre-built templates voor verschillende campagne fases
- Merge fields voor personalisatie
- Multi-language support
- HTML en plain text versies

### AI Email Generator (`modules/ai_email_generator.py`)
- OpenAI GPT-4 integratie
- Context-aware content generatie
- Tone en stijl aanpassing
- Template augmentation

### SendGrid Integration (`modules/sendgrid_integration.py`)
- Transactionele email verzending
- Template management
- Tracking pixels
- Webhook event handling

### Response Tracker (`modules/response_tracker.py`)
- Gmail API integratie
- Automatische reply detectie
- Thread matching
- Sentiment analyse

### Analytics (`modules/analytics.py`)
- KPI berekeningen
- Conversion tracking
- ROI projecties
- Funnel analyse

### Supabase Client (`modules/supabase_client.py`)
- CRUD operations
- Real-time subscriptions
- Bulk operations
- Error handling

---

## 🗄️ Database Schema

### `practices` table
```sql
CREATE TABLE practices (
  nr SERIAL PRIMARY KEY,
  naam VARCHAR(255) NOT NULL,
  gemeente VARCHAR(100),
  email VARCHAR(255),
  tel VARCHAR(50),
  website VARCHAR(255),
  riziv VARCHAR(50),
  artsen TEXT[],
  status VARCHAR(50) DEFAULT 'Nieuw',
  workflow JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Workflow Schema (JSONB)
```json
{
  "emails_sent": 0,
  "last_email_date": "2024-12-01T10:00:00Z",
  "last_email_template": "initial_outreach",
  "last_contact": "2024-12-01",
  "status": "Contacted",
  "next_action": "Follow-up",
  "replied": false,
  "reply_date": null
}
```

---

## 💻 Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints waar mogelijk
- Documenteer functies met docstrings
- Keep functions small en focused

### Testing
```bash
# Run tests (indien aanwezig)
pytest

# Code linting
flake8 .

# Type checking
mypy app.py
```

### Debug Mode
```bash
export FLASK_DEBUG=True
python app.py
```

---

## 🚢 Deployment

### Production Checklist
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production Supabase
- [ ] Set up email sending limits
- [ ] Enable HTTPS
- [ ] Configure error monitoring
- [ ] Set up backup strategy
- [ ] Review rate limits

### Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (optioneel)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

---

## 🔧 Troubleshooting

### Email niet verzonden
- Check SendGrid API key
- Verify email templates
- Check daily email limit
- Review logs: `tail -f logs/campaign.log`

### Database connectie errors
- Verify Supabase credentials
- Check network connectivity
- Review Supabase project status
- Fallback werkt met local JSON

### Gmail API errors
- Re-run `setup_gmail.py`
- Check `token.json` permissions
- Verify OAuth scopes
- Check Gmail API quota

### Scraping fails
- Website structure may have changed
- Check internet connection
- Review rate limiting
- Verify BeautifulSoup selectors

---

## 🤝 Contributing

Contributies zijn welkom! Volg deze stappen:

1. **Fork** het project
2. **Clone** jouw fork
   ```bash
   git clone https://github.com/jouw-username/CRM.git
   ```
3. **Maak een feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
4. **Commit** je wijzigingen
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
5. **Push** naar de branch
   ```bash
   git push origin feature/AmazingFeature
   ```
6. **Open een Pull Request**

### Commit Message Conventie
Gebruik [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` nieuwe feature
- `fix:` bug fix
- `docs:` documentatie wijzigingen
- `style:` formatting
- `refactor:` code refactoring
- `test:` tests toevoegen
- `chore:` maintenance

---

## 📄 License

Dit project is gelicenseerd onder de MIT License - zie het [LICENSE](LICENSE) bestand voor details.

---

## 👨‍💻 Authors

**Artur Gabrielian**
- GitHub: [@Boyov69](https://github.com/Boyov69)
- Email: artur@zorgcore.be

---

## 🙏 Acknowledgments

- SendGrid voor email delivery
- OpenAI voor AI capabilities
- Supabase voor database infrastructure
- Flask community voor het framework

---

## 📞 Support

Voor vragen of support:
- Open een [GitHub Issue](https://github.com/Boyov69/CRM/issues)
- Email: artur@zorgcore.be

---

**Gemaakt met ❤️ voor betere healthcare communicatie**
