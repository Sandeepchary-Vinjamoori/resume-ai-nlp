# Supabase Setup Guide

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" 
3. Sign up/in with GitHub
4. Click "New Project"
5. Choose organization and enter:
   - **Name**: `resume-ai`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to you
6. Click "Create new project"

## Step 2: Get API Keys

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public** key
   - **service_role** key (keep this secret!)

## Step 3: Configure Environment

1. Create `.env` file in your `resume_ai` folder:
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_public_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Flask Configuration  
SECRET_KEY=your_random_secret_key_here
FLASK_ENV=development
```

## Step 4: Set Up Database Tables

The app will automatically create tables, but you can also run this SQL in Supabase SQL Editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    provider VARCHAR(50) DEFAULT 'email',
    provider_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    style VARCHAR(50) DEFAULT 'modern',
    form_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_updated_at ON resumes(updated_at DESC);
```

## Step 5: Configure Google OAuth (Optional)

1. In Supabase dashboard, go to **Authentication** → **Providers**
2. Enable **Google** provider
3. Go to [Google Cloud Console](https://console.cloud.google.com/)
4. Create new project or select existing
5. Enable **Google+ API**
6. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
7. Set **Authorized redirect URIs**:
   ```
   https://your-project-id.supabase.co/auth/v1/callback
   ```
8. Copy **Client ID** and **Client Secret** to Supabase Google provider settings
9. Save configuration

## Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 7: Test the Setup

1. Run the app:
```bash
python app.py
```

2. Visit `http://localhost:5000`
3. Try creating an account
4. Check Supabase dashboard → **Authentication** → **Users** to see if user was created

## Troubleshooting

### Common Issues:

1. **"Supabase client not available"**
   - Check your `.env` file exists and has correct values
   - Verify SUPABASE_URL and SUPABASE_KEY are set

2. **Database connection errors**
   - Ensure your Supabase project is active
   - Check if you're using the correct database URL

3. **Google OAuth not working**
   - Verify redirect URI matches exactly
   - Check Google Cloud Console project settings
   - Ensure Google+ API is enabled

### Fallback Mode:
If Supabase isn't working, the app will automatically fall back to SQLite with local authentication. You'll see this message in logs:
```
Supabase credentials not found. Using SQLite fallback.
```

## Production Deployment

For production:
1. Set environment variables on your hosting platform
2. Use Row Level Security (RLS) in Supabase:
   ```sql
   ALTER TABLE users ENABLE ROW LEVEL SECURITY;
   ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
   
   -- Users can only see their own data
   CREATE POLICY "Users can view own profile" ON users
   FOR SELECT USING (auth.uid() = id);
   
   -- Users can only manage their own resumes
   CREATE POLICY "Users can manage own resumes" ON resumes
   FOR ALL USING (auth.uid() = user_id);
   ```
3. Enable email confirmations in Supabase Auth settings
4. Set up custom SMTP for emails (optional)

## Benefits You Get:

✅ **PostgreSQL Database** - Reliable, scalable
✅ **Built-in Authentication** - Email + Google OAuth  
✅ **Real-time Updates** - Future feature potential
✅ **Automatic Backups** - Supabase handles this
✅ **Dashboard & Analytics** - Built-in admin panel
✅ **API Auto-generation** - REST + GraphQL APIs
✅ **Edge Functions** - Serverless functions if needed

Your resume data will be stored securely with proper relationships and full ACID compliance!