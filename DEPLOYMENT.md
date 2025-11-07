# Deployment Guide for Virtual Partner

This guide will help you deploy your Virtual Partner application to various platforms.

## Prerequisites

1. **Environment Variables** - You need to set up these environment variables:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `SUPABASE_URL` (optional) - Your Supabase project URL
   - `SUPABASE_KEY` (optional) - Your Supabase API key

## Deployment Options

### Option 1: Render (Recommended - Free Tier Available)

1. **Create a Render Account**
   - Go to [render.com](https://render.com)
   - Sign up for a free account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or push code to GitHub first)

3. **Configure the Service**
   - **Name**: virtual-partner (or your preferred name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or choose a paid plan)

4. **Set Environment Variables**
   - Go to "Environment" tab
   - Add these variables:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     SUPABASE_URL=your_supabase_url (optional)
     SUPABASE_KEY=your_supabase_key (optional)
     PORT=10000
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your app will be live at `https://your-app-name.onrender.com`

### Option 2: Railway

1. **Create a Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   - Go to "Variables" tab
   - Add:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     SUPABASE_URL=your_supabase_url (optional)
     SUPABASE_KEY=your_supabase_key (optional)
     ```

4. **Deploy**
   - Railway will auto-detect Python and deploy
   - Your app will be live at `https://your-app-name.up.railway.app`

### Option 3: Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set GEMINI_API_KEY=your_gemini_api_key_here
   heroku config:set SUPABASE_URL=your_supabase_url
   heroku config:set SUPABASE_KEY=your_supabase_key
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Open App**
   ```bash
   heroku open
   ```

### Option 4: PythonAnywhere

1. **Create Account**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Sign up for free account

2. **Upload Files**
   - Go to "Files" tab
   - Upload all project files

3. **Create Web App**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose Flask and Python 3.10
   - Set source code directory

4. **Configure WSGI File**
   - Edit the WSGI file to point to your app:
   ```python
   import sys
   path = '/home/yourusername/your-app-name'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

5. **Set Environment Variables**
   - In "Web" tab → "Environment variables"
   - Add your API keys

6. **Reload Web App**
   - Click the green "Reload" button

## Database Setup (Optional but Recommended)

For persistent data storage, set up Supabase:

1. **Create Supabase Account**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project

2. **Create Tables**
   Run these SQL commands in Supabase SQL Editor:

   ```sql
   -- Users table
   CREATE TABLE users (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       username TEXT UNIQUE NOT NULL,
       password TEXT NOT NULL,
       gender TEXT DEFAULT 'other',
       bot_name TEXT DEFAULT 'Virtual Partner',
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Chats table
   CREATE TABLE chats (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       user_id UUID REFERENCES users(id) ON DELETE CASCADE,
       messages JSONB DEFAULT '[]'::jsonb,
       updated_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

3. **Get Credentials**
   - Go to Project Settings → API
   - Copy your URL and anon key
   - Add them as environment variables

## Post-Deployment Checklist

- [ ] Test registration and login
- [ ] Test chat functionality
- [ ] Verify bot name appears in header
- [ ] Check that gender-based personality works
- [ ] Test that old connection messages are filtered
- [ ] Verify environment variables are set correctly

## Troubleshooting

### App won't start
- Check that `gunicorn` is in requirements.txt
- Verify PORT environment variable is set
- Check logs for errors

### API calls failing
- Ensure CORS is properly configured
- Check that API_BASE_URL in index.html uses relative paths
- Verify backend is running

### Database errors
- Check Supabase credentials
- Verify tables are created
- Check connection in Supabase dashboard

## Support

If you encounter issues, check:
- Application logs in your hosting platform
- Browser console for frontend errors
- Network tab for API call issues

