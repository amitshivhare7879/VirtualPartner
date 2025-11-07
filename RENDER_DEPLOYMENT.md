# Deploy to Render - Step by Step Guide

## Prerequisites

1. **GitHub Account** - You need a GitHub account
2. **Render Account** - Sign up at [render.com](https://render.com) (free tier available)
3. **API Keys Ready**:
   - Google Gemini API Key
   - (Optional) Supabase URL and Key

## Step 1: Prepare Your Code

### 1.1 Initialize Git Repository (if not already done)

```bash
# Navigate to your project directory
cd E:\VirtualPartner

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"
```

### 1.2 Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click "New" to create a new repository
3. Name it: `virtual-partner` (or your preferred name)
4. **Don't** initialize with README (you already have files)
5. Click "Create repository"

### 1.3 Push to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/virtual-partner.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note**: Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 2: Deploy on Render

### 2.1 Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended) or email

### 2.2 Create New Web Service

1. Once logged in, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect account"** if prompted to connect GitHub
4. Select your repository: `virtual-partner` (or your repo name)
5. Click **"Connect"**

### 2.3 Configure the Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `virtual-partner` (or your preferred name)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main` (or `master` if that's your branch)
- **Root Directory**: Leave empty (or `.` if needed)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Plan:**
- Select **"Free"** plan (or choose a paid plan if needed)

### 2.4 Set Environment Variables

Click on **"Environment"** tab and add these variables:

**Required:**
```
GEMINI_API_KEY
```
Value: Your Google Gemini API key

**Optional (but recommended for data persistence):**
```
SUPABASE_URL
```
Value: Your Supabase project URL

```
SUPABASE_KEY
```
Value: Your Supabase anon/public key

**Note**: Render will automatically set the `PORT` variable, so you don't need to set it manually.

### 2.5 Deploy

1. Scroll down and click **"Create Web Service"**
2. Render will start building and deploying your app
3. Wait for deployment to complete (usually 2-5 minutes)
4. You'll see build logs in real-time

### 2.6 Verify Deployment

1. Once deployment is complete, you'll see a green "Live" status
2. Click on your service URL (e.g., `https://virtual-partner.onrender.com`)
3. Your app should be live!

## Step 3: Test Your Deployment

1. **Test Registration**:
   - Go to your deployed URL
   - Click "Need an account? Register"
   - Fill in:
     - Username
     - Password
     - Your Gender
     - Bot Name
   - Click "Create Account"

2. **Test Chat**:
   - After registration, try sending a message
   - Verify the bot responds with its name
   - Check that the bot's personality matches the opposite gender

3. **Test Login**:
   - Log out and log back in
   - Verify chat history loads (if using Supabase)

## Troubleshooting

### Build Fails

**Error: "Module not found"**
- Check that all dependencies are in `requirements.txt`
- Verify Python version in `runtime.txt` matches Render's supported versions

**Error: "Command not found: gunicorn"**
- Verify `gunicorn==21.2.0` is in `requirements.txt`

### App Won't Start

**Error: "Port already in use"**
- Render sets PORT automatically, don't override it
- Check that your code uses `os.environ.get('PORT', 5000)`

**Error: "Application failed to respond"**
- Check build logs for errors
- Verify `Procfile` contains: `web: gunicorn app:app`
- Ensure `app:app` matches your Flask app variable name

### API Calls Fail

**CORS Errors**:
- Verify `flask-cors` is installed
- Check that CORS is enabled in `app.py`: `CORS(app)`

**404 Errors**:
- Check that API routes start with `/api/`
- Verify frontend uses relative URLs: `window.location.origin + '/api'`

### Database Issues

**Supabase Connection Fails**:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
- Check that tables are created in Supabase
- Verify Supabase project is active

## Updating Your Deployment

When you make changes:

```bash
# Make your changes
# Then commit and push
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect the push and redeploy your app.

## Render Free Tier Limitations

- **Spins down after 15 minutes of inactivity** - First request after inactivity may take 30-60 seconds
- **750 hours/month** - Usually enough for personal projects
- **512 MB RAM** - Should be sufficient for this app
- **Auto-deploy from GitHub** - Enabled by default

## Next Steps

1. ✅ Set up Supabase for persistent data (optional but recommended)
2. ✅ Configure custom domain (if needed)
3. ✅ Set up monitoring/alerting
4. ✅ Review Render dashboard for usage stats

## Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Render Support**: Check Render dashboard for support options
- **Application Logs**: Available in Render dashboard under "Logs" tab

---

**Your app should now be live at**: `https://your-app-name.onrender.com` 🎉

