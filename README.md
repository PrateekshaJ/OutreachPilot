# 🚀 SynkSpace Outreach Pilot

AI-powered creator outreach and email campaign automation platform.
**Live Demo**: https://outreach-pilot-inky.vercel.app/

SynkSpace Outreach Pilot helps brands manage creator databases, launch personalized email campaigns, and track outreach performance from a single dashboard.

---

## ✨ Features

- 📊 Creator outreach dashboard
- 📁 CSV creator import
- 👥 Creator database management
- 💌 Personalized email campaigns
- 🎨 HTML email templates
- 📈 Campaign history & email logs
- ☁️ Cloud image hosting
- 🚀 Production deployment

---

## 🛠️ Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS
- Axios

### Backend
- FastAPI
- Python
- Pydantic

### Database
- MongoDB Atlas

### Services
- Zoho SMTP (Email delivery)
- Cloudinary (Email assets)

### Deployment
- Frontend → Vercel
- Backend → Railway

---

## 🏗️ Architecture


User
 ↓
React + Vite (Vercel)
 ↓
FastAPI Backend (Railway)
 ↓
MongoDB Atlas

Additional Services:
- Zoho SMTP → Email sending
- Cloudinary → Image delivery


---

## 📌 Workflow

1. Upload creator CSV
2. Store creator profiles in MongoDB
3. Create email campaign
4. Generate personalized HTML emails
5. Send emails through Zoho SMTP
6. Track campaign status

---

## 🚀 Status

Production deployed ✅
