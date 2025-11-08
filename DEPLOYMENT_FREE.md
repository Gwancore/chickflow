# 🚀 ChickFlow Deployment Guide (FREE Forever)

This guide will help you deploy ChickFlow to free cloud platforms so it's accessible from anywhere.

## 📋 What You'll Get
- **Backend API**: Hosted on Render (free tier)
- **Frontend Web App**: Hosted on Vercel (free tier)
- **Access**: From any computer or phone worldwide
- **URL**: Professional URLs like `https://chickflow.vercel.app`

---

## 🔧 Prerequisites
1. GitHub account (free)
2. Render account (free) - Sign up at [render.com](https://render.com)
3. Vercel account (free) - Sign up at [vercel.com](https://vercel.com)

---

## Part 1: Deploy Backend to Render (15 minutes)

### Step 1: Push Code to GitHub
```bash
cd /home/gwancore/Documents/beams
git init
git add .
git commit -m "Initial commit"
# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/chickflow.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `chickflow-api`
   - **Region**: Choose closest to you
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

5. Add Environment Variables (click "Advanced"):
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = (click "Generate" or use any random string)
   - `DATABASE_URL` = `sqlite:///instance/chickflow.db`
   - `PYTHON_VERSION` = `3.11.0`

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. **Copy your backend URL** (e.g., `https://chickflow-api.onrender.com`)

### Step 3: Initialize Database
Once deployed, go to your Render dashboard:
1. Click on your service → **"Shell"** tab
2. Run these commands:
```bash
python -c "from app import create_app, db; from models import User; from werkzeug.security import generate_password_hash; app = create_app(); app.app_context().push(); db.create_all(); admin = User(username='admin', email='admin@chickflow.com', role='Admin'); admin.password_hash = generate_password_hash('admin123'); db.session.add(admin); db.session.commit(); print('Database created!')"
```

---

## Part 2: Deploy Frontend to Vercel (10 minutes)

### Step 1: Configure Frontend
1. In your local project, create `.env` file in `frontend/` folder:
```bash
echo "VITE_API_URL=https://your-backend-url.onrender.com" > frontend/.env
```
Replace `your-backend-url.onrender.com` with your actual Render URL from Part 1.

2. Commit and push:
```bash
git add .
git commit -m "Add production config"
git push
```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variable:
   - `VITE_API_URL` = Your Render backend URL (e.g., `https://chickflow-api.onrender.com`)

6. Click **"Deploy"**
7. Wait 2-3 minutes
8. **Copy your frontend URL** (e.g., `https://chickflow.vercel.app`)

---

## Part 3: Enable CORS (Important!)

Your backend needs to allow requests from your frontend:

1. Go to Render dashboard → Your service → **"Environment"**
2. Add environment variable:
   - `FRONTEND_URL` = Your Vercel URL (e.g., `https://chickflow.vercel.app`)

3. The app is already configured to use this in `backend/app.py`

---

## 🎉 You're Live!

### Access Your App:
- **Web App**: `https://your-app.vercel.app`
- **API**: `https://your-api.onrender.com`

### Login Credentials:
- Username: `admin`
- Password: `admin123`

### Share Access:
Anyone can access your app from anywhere using the Vercel URL. Just share the link!

---

## 🔄 Updating Your App

Whenever you make changes:
```bash
git add .
git commit -m "Description of changes"
git push
```
Both Render and Vercel will automatically redeploy!

---

## ⚠️ Important Notes

### Free Tier Limitations:
- **Render Free**: 
  - App sleeps after 15 min of inactivity (first request takes 30-60s to wake up)
  - 750 hours/month (enough for 24/7 with one app)
  - SQLite database (good for small teams, resets on redeploy)

- **Vercel Free**: 
  - Unlimited bandwidth
  - 100GB bandwidth/month
  - Perfect for small to medium teams

### Upgrading Database (Optional):
For a persistent database, add PostgreSQL on Render:
1. In Render dashboard → **"New +"** → **"PostgreSQL"**
2. Create database (free tier available)
3. Copy the "Internal Database URL"
4. Update `DATABASE_URL` environment variable in your web service
5. Re-run the database initialization command

---

## 🆘 Troubleshooting

### Backend not responding:
- Check Render logs: Dashboard → Service → "Logs" tab
- Verify environment variables are set correctly

### Frontend can't connect to backend:
- Check `VITE_API_URL` in Vercel environment variables
- Verify CORS is enabled in backend

### Database issues:
- Re-run database initialization in Render Shell
- Check logs for SQLAlchemy errors

---

## 📞 Support
If you encounter issues, check:
- Render logs for backend errors
- Browser console (F12) for frontend errors
- Ensure all environment variables are set correctly

---

**Congratulations! Your ChickFlow app is now accessible worldwide! 🌍**
