# 🚀 Quick Start Guide

Get your CRM up and running in 5 minutes!

## Prerequisites

Make sure you have installed:
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 14+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

Check versions:
```bash
python3 --version
node --version
npm --version
git --version
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Boyov69/CRM.git
cd CRM
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor
nano .env
# or
code .env
```

**Minimum required configuration:**
```env
SECRET_KEY=your-random-secret-key-change-this
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

### 3. Start Development Servers

**Option A: One Command (Easiest)**
```bash
./dev.sh
```

**Option B: Manual (More Control)**

Terminal 1 - Backend:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd backend
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application

Open your browser and go to:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Health Check:** http://localhost:5000/health

## First Steps

### 1. Add Your First Practice

Click **Praktijken** → **Nieuwe Praktijk** and fill in:
- Naam: Practice name
- Gemeente: City/municipality
- Email: Contact email
- Telefoon: Phone number

### 2. Search for Leads

Go to **Leads** tab:
1. Enter a municipality name (e.g., "Brussel", "Antwerpen")
2. Click **Zoeken**
3. Click **Toevoegen** to add practices to your database

### 3. Start a Campaign

Navigate to **Campagnes**:
1. Select email template
2. Toggle AI personalization (optional)
3. Click **Start Campagne**

### 4. View Analytics

Check **Dashboard** and **Analytics** for:
- Campaign statistics
- Conversion rates
- ROI projections
- Funnel analysis

## Configuration Options

### Email Providers

**SendGrid (Recommended)**
```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@domain.com
```

**Gmail**
```env
EMAIL_PROVIDER=gmail
# Download credentials.json from Google Cloud Console
# Place in project root
```

**SMTP**
```env
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Database

**Supabase (Recommended for Production)**
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**JSON (Good for Development)**
No configuration needed - automatic fallback to `data/practices.json`

### AI Features

**OpenAI GPT-4**
```env
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4
```

### Notifications

**Slack**
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

## Common Commands

### Development
```bash
# Start everything
./dev.sh

# Backend only
cd backend && python app.py

# Frontend only
cd frontend && npm run dev

# Install new Python package
pip install package-name
pip freeze > requirements.txt

# Install new npm package
cd frontend && npm install package-name
```

### Testing
```bash
# Test backend API
curl http://localhost:5000/health
curl http://localhost:5000/api/practices

# View logs
tail -f logs/campaign.log
```

### Production
```bash
# Backend
gunicorn -w 4 -b 0.0.0.0:8000 backend.app:create_app()

# Frontend
cd frontend
npm run build
# Serve from frontend/dist/
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>

# Or use different port
# In backend/app.py change: app.run(port=5001)
# In frontend/vite.config.js change: server.port: 3001
```

### Dependencies Won't Install
```bash
# Python
python3 -m pip install --upgrade pip
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node
rm -rf frontend/node_modules
cd frontend
npm cache clean --force
npm install
```

### CORS Errors
Ensure:
1. Backend is running on port 5000
2. Frontend proxy is configured in `frontend/vite.config.js`
3. CORS is enabled in `backend/app.py`

### Email Sending Fails
1. Check `.env` has correct `SENDGRID_API_KEY`
2. Verify SendGrid account is active
3. Check logs: `tail -f logs/campaign.log`
4. Test with curl:
```bash
curl -X POST http://localhost:5000/api/campaigns/start \
  -H "Content-Type: application/json" \
  -d '{"ids":[1],"template":"initial_outreach","use_ai":false}'
```

## Next Steps

1. **Read Full Documentation:** [README.md](README.md)
2. **Development Guide:** [README-DEV.md](README-DEV.md)
3. **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Changelog:** [CHANGELOG.md](CHANGELOG.md)

## Getting Help

- **GitHub Issues:** https://github.com/Boyov69/CRM/issues
- **Email Support:** artur@zorgcore.be
- **Documentation:** Check README files in project

## Tips for Success

1. **Start Small:** Test with 2-3 practices first
2. **Use AI Sparingly:** AI emails cost money, use for important campaigns
3. **Monitor Logs:** Check `logs/campaign.log` regularly
4. **Backup Data:** If using JSON, backup `data/practices.json`
5. **Rate Limits:** Respect SendGrid daily limits
6. **Test Emails:** Send to yourself first before real campaign

---

**Happy CRM-ing! 🎉**
