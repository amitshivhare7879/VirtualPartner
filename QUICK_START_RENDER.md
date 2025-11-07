# Quick Start: Deploy to Render in 5 Minutes

## Prerequisites Checklist
- [ ] GitHub account
- [ ] Render account (sign up at render.com)
- [ ] Google Gemini API key

## Step 1: Initialize Git (2 minutes)

### Option A: Use the batch script (Windows)
1. Double-click `setup_render.bat`
2. Follow the prompts

### Option B: Manual commands
Open PowerShell/Terminal in your project folder and run:

```bash
git init
git add .
git commit -m "Initial commit - Ready for Render deployment"
```

## Step 2: Push to GitHub (2 minutes)

1. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Repository name: `virtual-partner`
   - **Don't** check "Initialize with README"
   - Click "Create repository"

2. **Push your code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/virtual-partner.git
   git branch -M main
   git push -u origin main
   ```
   Replace `YOUR_USERNAME` with your GitHub username.

## Step 3: Deploy on Render (1 minute)

1. **Go to Render**: https://render.com
2. **Sign up/Login** (use GitHub for easy connection)
3. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account if needed
   - Select repository: `virtual-partner`
   - Click "Connect"

4. **Configure**:
   - **Name**: `virtual-partner` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: `Free`

5. **Environment Variables** (click "Environment" tab):
   ```
   GEMINI_API_KEY = your_gemini_api_key_here
   ```
   (Optional: Add SUPABASE_URL and SUPABASE_KEY if using Supabase)

6. **Deploy**:
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - Your app will be live at: `https://virtual-partner.onrender.com`

## ✅ Done!

Your app is now live! Test it by:
1. Opening the URL
2. Registering a new account
3. Testing the chat

## Common Issues

**Build fails?**
- Check that all files are committed
- Verify `requirements.txt` has all dependencies
- Check Render logs for specific errors

**App won't start?**
- Verify `Procfile` exists with: `web: gunicorn app:app`
- Check that `gunicorn` is in `requirements.txt`
- Review logs in Render dashboard

**Need help?**
- See `RENDER_DEPLOYMENT.md` for detailed guide
- Check Render logs in dashboard
- Review application logs

---

**Total time: ~5 minutes** ⚡

