# 🚀 SPRINT 2 - OMNICHANNEL COMMUNICATIE

**Branch:** `feature/sprint2-omnichannel`  
**Duration:** 2-3 weeks  
**Goal:** Multi-channel communicatie (SMS + WhatsApp + Unified Inbox)

---

## 🎯 OBJECTIVES

Transform CRM into **omnichannel communication platform** waar je praktijken bereikt via hun preferred channel:

✅ **SMS Integration** - Instant tekstberichten via Twilio  
✅ **WhatsApp Business** - Bereik via #1 channel in België  
✅ **Unified Inbox** - Alle communicatie op 1 plek  
✅ **Multi-Channel Campaigns** - Email → SMS → WhatsApp flows  

---

## 📋 FEATURES

### **Phase 1: SMS Foundation** (Week 1)

#### 1.1 Twilio SMS Integration
**Backend:**
- `backend/services/sms_service.py` - Twilio API wrapper
- `backend/api/sms_api.py` - SMS endpoints
- SMS sending (single & bulk)
- Delivery tracking (sent, delivered, failed)
- SMS history per practice
- Cost tracking per SMS

**Endpoints:**
```python
POST   /api/sms/send              # Send single SMS
POST   /api/sms/bulk              # Send bulk SMS
GET    /api/sms/history/:id       # SMS history for practice
GET    /api/sms/templates         # Get SMS templates
POST   /api/sms/templates         # Create SMS template
```

**Frontend:**
- SMS compose modal
- SMS history view
- SMS templates library

---

#### 1.2 SMS Templates System
**Features:**
- Pre-defined templates (intro, follow-up, reminder, etc.)
- Variable substitution: `{naam}`, `{gemeente}`, `{email}`
- Template categories
- Character count & cost estimation
- Template testing

**Templates:**
```
1. Initial Contact
   "Hallo {naam}, we helpen praktijken met..."
   
2. Follow-up
   "Beste {naam}, heb je onze vorige email gezien?"
   
3. Meeting Reminder
   "Reminder: onze afspraak morgen om {tijd}"
   
4. Special Offer
   "Exclusief aanbod voor praktijken in {gemeente}"
```

---

#### 1.3 SMS Analytics
**Metrics:**
- Delivery rate (delivered/sent)
- Response rate (if 2-way SMS)
- Cost per SMS
- Cost per campaign
- Click-through rate (if URLs included)
- Best time to send

---

### **Phase 2: WhatsApp Business** (Week 1-2)

#### 2.1 WhatsApp Integration
**Backend:**
- `backend/services/whatsapp_service.py` - Twilio WhatsApp API
- `backend/api/whatsapp_api.py` - WhatsApp endpoints
- Template message sending
- Media support (images, PDFs)
- Status tracking (sent, delivered, read)
- Webhook handler for responses

**Endpoints:**
```python
POST   /api/whatsapp/send         # Send WhatsApp message
POST   /api/whatsapp/send-media   # Send with image/PDF
GET    /api/whatsapp/history/:id  # WhatsApp history
GET    /api/whatsapp/templates    # Approved templates
POST   /api/whatsapp/webhook      # Receive responses
```

**WhatsApp Features:**
- Pre-approved message templates
- Rich media (images, documents)
- Read receipts
- 2-way conversations
- Quick replies

---

#### 2.2 WhatsApp Templates
**Template Management:**
- Submit templates for Facebook approval
- Template status tracking (pending, approved, rejected)
- Template categories (marketing, transactional, utility)
- Variable placeholders
- Media attachments

**Example Templates:**
```
1. Introduction (Marketing)
   "Hallo {{1}}, wij helpen huisartspraktijken met..."
   [Button: Meer Info]
   
2. Appointment Confirmation (Transactional)
   "Uw afspraak op {{1}} om {{2}} is bevestigd."
   
3. Document Share (Utility)
   "Hier is het document dat u heeft aangevraagd."
   [PDF attachment]
```

---

### **Phase 3: Unified Inbox** (Week 2)

#### 3.1 Inbox Architecture
**Backend:**
- `backend/services/inbox_service.py` - Unified message aggregator
- Combine email + SMS + WhatsApp threads
- Conversation grouping by practice
- Real-time updates via WebSocket
- Unread count tracking
- Search & filter

**Endpoints:**
```python
GET    /api/inbox/conversations   # All conversations
GET    /api/inbox/conversation/:id # Single conversation thread
POST   /api/inbox/reply           # Reply to message
GET    /api/inbox/unread          # Unread count
PUT    /api/inbox/mark-read/:id   # Mark as read
```

**Conversation Object:**
```json
{
  "id": "conv_123",
  "practice_id": 1,
  "practice_name": "Huisartsenpraktijk ABC",
  "channels": ["email", "sms", "whatsapp"],
  "last_message": {
    "id": "msg_456",
    "channel": "whatsapp",
    "direction": "inbound",
    "content": "Ja, ik ben geïnteresseerd",
    "timestamp": "2024-01-15T10:30:00Z",
    "read": false
  },
  "unread_count": 3,
  "messages": [...]
}
```

---

#### 3.2 Inbox Frontend
**Components:**
- Conversation list (left sidebar)
- Message thread view (center)
- Quick reply composer (bottom)
- Channel selector (email/SMS/WhatsApp)
- Rich media viewer
- Search & filters

**Features:**
- Channel badges (📧 Email, 📱 SMS, 💬 WhatsApp)
- Unread indicators
- Real-time updates
- Quick actions (archive, mark as read)
- Emoji reactions
- File attachments

---

### **Phase 4: Multi-Channel Campaigns** (Week 2-3)

#### 4.1 Campaign Builder
**Backend:**
- `backend/services/campaign_service.py` - Multi-channel orchestration
- Campaign workflow engine
- Channel sequencing (Email → Wait → SMS → Wait → WhatsApp)
- Fallback logic (if email bounces → SMS)
- Channel preference per practice
- A/B testing per channel

**Campaign Flow Example:**
```
Step 1: Send Email
  ↓ wait 2 days
Step 2: If not opened → Send SMS
  ↓ wait 1 day
Step 3: If not responded → Send WhatsApp
  ↓ wait 3 days
Step 4: If still no response → Mark as cold lead
```

**Endpoints:**
```python
POST   /api/campaigns/create      # Create campaign
GET    /api/campaigns/list        # List campaigns
GET    /api/campaigns/:id         # Campaign details
POST   /api/campaigns/:id/start   # Start campaign
GET    /api/campaigns/:id/stats   # Campaign analytics
```

---

#### 4.2 Campaign Analytics
**Metrics:**
- Total sent per channel
- Open/delivery rates per channel
- Response rate per channel
- Conversion rate
- Cost per conversion
- Best performing channel
- Channel preference insights

**Dashboard:**
- Funnel visualization
- Channel comparison chart
- Timeline view
- ROI calculator

---

## 🏗️ TECHNICAL ARCHITECTURE

### **Backend Structure**
```
backend/
├── services/
│   ├── sms_service.py           # Twilio SMS API
│   ├── whatsapp_service.py      # Twilio WhatsApp API
│   ├── inbox_service.py         # Unified inbox aggregator
│   ├── campaign_service.py      # Multi-channel campaigns
│   └── notification_service.py  # Real-time notifications
├── api/
│   ├── sms_api.py              # SMS endpoints
│   ├── whatsapp_api.py         # WhatsApp endpoints
│   ├── inbox_api.py            # Inbox endpoints
│   └── campaign_api.py         # Campaign endpoints
└── models/
    ├── message.py              # Message model
    ├── conversation.py         # Conversation model
    └── campaign.py             # Campaign model
```

### **Frontend Structure**
```
frontend/src/
├── pages/
│   ├── Inbox.jsx               # Unified inbox page
│   ├── Campaigns.jsx           # Campaign builder (enhanced)
│   └── Analytics.jsx           # Analytics dashboard (enhanced)
├── components/
│   ├── inbox/
│   │   ├── ConversationList.jsx
│   │   ├── MessageThread.jsx
│   │   ├── ReplyComposer.jsx
│   │   └── ChannelBadge.jsx
│   ├── sms/
│   │   ├── SMSComposer.jsx
│   │   ├── SMSTemplate.jsx
│   │   └── SMSHistory.jsx
│   └── whatsapp/
│       ├── WhatsAppComposer.jsx
│       ├── WhatsAppTemplate.jsx
│       └── MediaUploader.jsx
└── hooks/
    ├── useInbox.js
    ├── useSMS.js
    └── useWhatsApp.js
```

---

## 🔧 DEPENDENCIES

### **Backend (New)**
```txt
twilio>=8.10.0              # SMS & WhatsApp API
python-dotenv>=1.0.0        # Environment variables
websockets>=12.0            # Real-time updates
celery>=5.3.4               # Background tasks
redis>=5.0.0                # Task queue & caching
```

### **Frontend (New)**
```json
{
  "socket.io-client": "^4.7.0",     // Real-time updates
  "emoji-picker-react": "^4.5.0",   // Emoji support
  "react-dropzone": "^14.2.0"       // File uploads
}
```

---

## 📊 TWILIO SETUP VEREIST

### **Accounts Needed:**
1. **Twilio Account** (gratis trial: $15 credit)
   - SMS capable phone number
   - WhatsApp sandbox (gratis) of Business API ($$$)
   
### **Configuration:**
```bash
# .env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+32xxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886  # Sandbox
```

---

## 🎯 SUCCESS METRICS

### **Sprint 2 Goals:**
- ✅ SMS integration werkend
- ✅ WhatsApp messages versturen
- ✅ Unified inbox met 3 channels
- ✅ Multi-channel campaign builder
- ✅ Real-time message updates
- ✅ 80%+ delivery rate across channels

### **Business Impact:**
- 📈 +50% response rate (SMS/WhatsApp > Email)
- 💰 Lower cost per conversion
- ⚡ Faster lead engagement
- 🎯 Better channel targeting

---

## 🚀 DEVELOPMENT PHASES

### **Week 1: Foundation**
- Day 1-2: Twilio setup + SMS service
- Day 3: SMS API endpoints
- Day 4-5: WhatsApp service + API

### **Week 2: Inbox & UI**
- Day 1-2: Unified inbox backend
- Day 3-4: Inbox frontend
- Day 5: Real-time updates

### **Week 3: Campaigns & Polish**
- Day 1-2: Multi-channel campaigns
- Day 3: Campaign analytics
- Day 4-5: Testing + documentation

---

## 🔥 COMPETITIVE ADVANTAGE

**After Sprint 2:**

| Feature | Our CRM | Salesforce | HubSpot | Pipedrive |
|---------|---------|------------|---------|-----------|
| SMS Integration | ✅ | ✅ ($$$) | ✅ ($$) | ⚠️ Add-on |
| WhatsApp Business | ✅ | ⚠️ Limited | ⚠️ Beta | ❌ |
| Unified Inbox | ✅ | ✅ ($$$) | ✅ ($$) | ❌ |
| Multi-Channel Campaigns | ✅ | ✅ ($$$) | ✅ ($$) | ⚠️ Basic |
| Healthcare Focus | ✅ | ❌ | ❌ | ❌ |
| **Price** | **€0** | **€200+/user** | **€120/user** | **€60/user** |

**We blijven 2+ jaar voorop!** 🚀

---

## ✅ READY TO START!

**Eerste stap:** Twilio SMS Integration

Let's build! 💪
