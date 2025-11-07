# Virtual Partner - AI Chatbot Application

A caring, empathetic virtual partner chatbot built with Flask and Google Gemini AI. Features gender-aware personality, customizable bot names, and persistent conversation history.

## Features

- 🤖 **AI-Powered Conversations** - Powered by Google Gemini AI
- 👤 **User Authentication** - Secure login and registration
- 🎭 **Gender-Aware Personality** - Bot adapts personality based on opposite gender
- ✏️ **Customizable Bot Name** - Name your virtual partner
- 💬 **Conversation History** - Persistent chat history with Supabase
- 🧠 **Smart Context Filtering** - Filters out old connection messages
- 💾 **Data Persistence** - Optional Supabase integration for data storage

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd VirtualPartner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SUPABASE_URL=your_supabase_url (optional)
   SUPABASE_KEY=your_supabase_key (optional)
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5000`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect GitHub repository
5. Set environment variables:
   - `GEMINI_API_KEY`
   - `SUPABASE_URL` (optional)
   - `SUPABASE_KEY` (optional)
6. Deploy!

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key |
| `SUPABASE_URL` | No | Supabase project URL for database |
| `SUPABASE_KEY` | No | Supabase API key |
| `PORT` | No | Server port (default: 5000) |

## Database Setup (Optional)

If using Supabase, create these tables:

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

## Project Structure

```
VirtualPartner/
├── app.py              # Flask backend application
├── index.html          # Frontend HTML/CSS/JavaScript
├── requirements.txt    # Python dependencies
├── Procfile           # Deployment configuration
├── runtime.txt        # Python version
├── .gitignore        # Git ignore rules
├── DEPLOYMENT.md     # Deployment guide
└── README.md         # This file
```

## API Endpoints

- `GET /` - Serve frontend
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/chat/message` - Send message and get AI response
- `GET /api/chat/history/<user_id>` - Get chat history
- `GET /api/health` - Health check

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Google Gemini API
- **Database**: Supabase (optional)
- **Deployment**: Gunicorn

## License

This project is open source and available for personal use.

## Support

For issues or questions, please check the deployment guide or review the application logs.

