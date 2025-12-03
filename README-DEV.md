# 🚀 Development Guide

## Project Structure

```
CRM/
├── backend/                 # Flask API Backend
│   ├── api/                # API endpoints (blueprints)
│   │   ├── practices.py    # Practice management routes
│   │   ├── campaigns.py    # Campaign routes
│   │   └── leads.py        # Lead generation routes
│   ├── services/           # Business logic layer
│   │   ├── database.py     # Database service
│   │   ├── email_service.py # Email sending
│   │   ├── analytics.py    # Analytics calculations
│   │   └── scraper.py      # Web scraping
│   ├── app.py              # Flask app factory
│   └── config.py           # Configuration
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
│
├── modules/               # Legacy shared modules
├── data/                  # Local JSON storage
└── logs/                  # Application logs
```

## Quick Start

### Option 1: One Command (Recommended)

```bash
./dev.sh
```

This script will:
1. Create Python virtual environment if needed
2. Install backend dependencies
3. Install frontend dependencies
4. Start both backend and frontend servers
5. Open the app in your browser

### Option 2: Manual Setup

#### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend server
cd backend
python app.py
```

Backend runs on: **http://localhost:5000**

#### Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

## API Endpoints

### Practices
- `GET /api/practices` - Get all practices
- `POST /api/practices` - Add new practice
- `GET /api/practices/<id>` - Get specific practice
- `PUT /api/practices/<id>` - Update practice
- `POST /api/practices/<id>/mark-replied` - Mark as replied

### Campaigns
- `POST /api/campaigns/start` - Start email campaign
- `GET /api/campaigns/stats` - Get campaign statistics

### Leads
- `POST /api/leads/search` - Search for leads
- `POST /api/leads/scrape` - Scrape practice details

### Health
- `GET /health` - Health check endpoint

## Development Workflow

### Backend Development

1. **Make changes** in `backend/` directory
2. **Flask auto-reloads** on file changes (when DEBUG=True)
3. **Check logs** in `logs/campaign.log`
4. **Test API** using curl, Postman, or frontend

Example:
```bash
# Test health endpoint
curl http://localhost:5000/health

# Get practices
curl http://localhost:5000/api/practices

# Add practice
curl -X POST http://localhost:5000/api/practices \
  -H "Content-Type: application/json" \
  -d '{"naam":"Test Practice","gemeente":"Brussel"}'
```

### Frontend Development

1. **Make changes** in `frontend/src/`
2. **Vite HMR** provides instant updates
3. **Check browser console** for errors
4. **Use React DevTools** for debugging

### Adding a New Feature

**Backend:**
1. Create new service in `backend/services/` if needed
2. Add routes in appropriate blueprint in `backend/api/`
3. Update service layer to handle business logic
4. Test endpoint with curl or Postman

**Frontend:**
1. Create component in `frontend/src/components/` or page in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx` if new page
3. Use axios to call backend API
4. Style with CSS classes from `index.css`

## Environment Variables

Required variables in `.env`:

```env
# Essential
SECRET_KEY=your-secret-key
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_FROM_EMAIL=your-email@domain.com

# Optional but recommended
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
OPENAI_API_KEY=your-openai-key
SLACK_WEBHOOK_URL=your-slack-webhook
```

## Database

### Supabase (Recommended)

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Get URL and anon key
4. Add to `.env`
5. Run migration: `python scripts/migrate_to_supabase.py`

### JSON Fallback

If Supabase not configured:
- Data stored in `data/practices.json`
- Automatic fallback
- Good for local development

## Testing

### Backend Tests

```bash
# Run tests (when available)
pytest

# With coverage
pytest --cov=backend

# Lint code
flake8 backend/
```

### Frontend Tests

```bash
cd frontend

# Run tests (when available)
npm test

# Lint
npm run lint
```

## Common Issues

### Backend won't start
- Check Python version (needs 3.8+)
- Verify virtual environment is activated
- Check if port 5000 is already in use
- Review logs in `logs/campaign.log`

### Frontend won't start
- Check Node version (needs 14+)
- Delete `node_modules` and reinstall
- Check if port 3000 is already in use
- Clear npm cache: `npm cache clean --force`

### API calls fail with CORS error
- Ensure backend is running
- Check proxy configuration in `frontend/vite.config.js`
- Verify CORS settings in `backend/app.py`

### Email sending fails
- Verify SendGrid API key in `.env`
- Check SendGrid account status
- Review email logs in database or logs file

## Production Build

### Backend

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.app:create_app()
```

### Frontend

```bash
cd frontend

# Build for production
npm run build

# Preview build
npm run preview

# Serve with any static server
# Build output is in frontend/dist/
```

## Tips & Tricks

### Hot Reload Not Working?

Backend: Set `FLASK_DEBUG=True` in `.env`
Frontend: Restart Vite dev server

### Database Reset

```bash
# Delete local data
rm data/practices.json

# Reset Supabase (be careful!)
# Use Supabase dashboard to truncate table
```

### View Logs

```bash
# Backend logs
tail -f logs/campaign.log

# Follow logs in real-time
tail -f logs/campaign.log | grep ERROR
```

### Quick API Test

```bash
# Health check
curl http://localhost:5000/health

# Get all practices
curl http://localhost:5000/api/practices | jq

# Start campaign (example)
curl -X POST http://localhost:5000/api/campaigns/start \
  -H "Content-Type: application/json" \
  -d '{"ids":[1,2],"template":"initial_outreach","use_ai":false}'
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Support

- GitHub Issues: https://github.com/Boyov69/CRM/issues
- Email: artur@zorgcore.be
