# SynkSpace Outreach Bot

An AI-powered creator outreach automation platform for sending personalized email campaigns to influencers.

## Purpose

SynkSpace Outreach Bot helps marketing teams and brand managers streamline influencer outreach. Upload creator lists via CSV, craft personalized HTML email templates with Jinja2 variables, and send campaigns at scale through Zoho SMTP — all tracked in a modern dashboard.

## Tech Stack

| Layer    | Technologies |
|----------|-------------|
| Frontend | React, Vite, Tailwind CSS, Axios, React Router |
| Backend  | Python, FastAPI, MongoDB (Motor), pandas, Jinja2, aiosmtplib |
| Email    | Zoho SMTP |
| Config   | python-dotenv |

## Project Structure

```
synkspace-outreach-bot/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment settings
│   ├── database.py          # MongoDB connection
│   ├── email_sender.py      # Zoho SMTP integration
│   ├── template_engine.py   # Jinja2 renderer
│   ├── routes/              # API endpoints
│   ├── models/              # Pydantic schemas
│   ├── templates/           # Sample HTML templates
│   └── uploads/             # Sample CSV data
├── frontend/
│   └── src/
│       ├── components/      # UI components
│       ├── pages/           # Route pages
│       └── api/             # Axios client
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)

### 1. Backend

```bash
cd synkspace-outreach-bot/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and Zoho SMTP credentials

# Start the server
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000` — you should see:

```
SynkSpace Outreach Bot Running 🚀
```

### 2. Frontend

```bash
cd synkspace-outreach-bot/frontend

npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 3. Zoho SMTP Setup

1. Log in to your [Zoho Mail](https://www.zoho.com/mail/) account.
2. Go to **Settings → Mail Accounts → SMTP**.
3. Generate an **App-Specific Password** (required for third-party apps).
4. Add credentials to `backend/.env`:

```env
ZOHO_EMAIL=your-email@zoho.com
ZOHO_PASSWORD=your-app-specific-password
SMTP_SERVER=smtp.zoho.com
SMTP_PORT=587
```

### 4. Upload Creators

1. Navigate to **Upload CSV** in the dashboard.
2. Upload a CSV with columns: `name`, `email`, `instagram`, `category`.
3. A sample file is provided at `backend/uploads/creators.csv`.

### 5. Send a Campaign

1. Go to **Campaigns**.
2. Enter a campaign name, email subject, and HTML template.
3. Use Jinja2 variables for personalization:

```html
<p>Hi {{ name }},</p>
<p>You are invited to join SynkSpace.</p>
<p>As a {{ category }} creator, we'd love to work with you.</p>
```

4. Click **Create & Send Campaign**.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health message |
| GET | `/api/emails/stats` | Dashboard statistics |
| GET | `/api/creators` | List all creators |
| POST | `/api/creators/upload` | Upload creator CSV |
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Create campaign |
| POST | `/api/campaigns/{id}/send` | Send campaign emails |
| GET | `/api/emails/logs` | Email send logs |

## Future AI Personalization Features

The platform is designed to evolve with AI-driven outreach capabilities:

- **AI-generated email copy** — Use LLMs to draft unique outreach messages per creator based on their Instagram bio, category, and engagement style.
- **Smart segmentation** — Automatically cluster creators by niche, audience size, and content tone for targeted campaigns.
- **Dynamic template suggestions** — Recommend subject lines and CTAs optimized for open and reply rates.
- **Reply sentiment analysis** — Classify influencer responses (interested, not interested, needs follow-up) and auto-route to the right workflow.
- **A/B testing** — Test multiple subject lines and templates, with AI selecting the winning variant.
- **Open & click tracking** — Embed tracking pixels and UTM links to replace the placeholder open rate metric.

## License

MIT
