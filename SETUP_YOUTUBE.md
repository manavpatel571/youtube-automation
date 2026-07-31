# YouTube API Setup Guide (One-Time)

Follow these steps to set up YouTube API credentials for automated video uploads.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top → **New Project**
3. Name it something like `AI Shorts Auto`
4. Click **Create**

## Step 2: Enable YouTube Data API v3

1. In your new project, go to **APIs & Services → Library**
2. Search for **YouTube Data API v3**
3. Click **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Select **External** → Click **Create**
3. Fill in:
   - App name: `AI Shorts Auto`
   - User support email: your email
   - Developer contact: your email
4. Click **Save and Continue** through Scopes (skip)
5. Under **Test Users**, click **Add Users** → add your Gmail address
6. Click **Save and Continue** → **Back to Dashboard**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Name: `auto-video-uploader`
5. Click **Create**
6. Click **Download JSON**
7. Save the file as: `credentials/client_secret.json` in this project

## Step 5: First Authentication

Run this command:
```bash
python main.py upload test
```

This will:
1. Open your browser
2. Ask you to sign in with your Google account
3. Grant permission to upload videos
4. Save a `credentials/token.json` (reused automatically for future uploads)

## Important Notes

- The OAuth consent screen is in **Testing mode** — only your added test user can authenticate
- Tokens expire periodically but auto-refresh
- **Never commit** `client_secret.json` or `token.json` to git
- YouTube API quota: 10,000 units/day (each upload = 1,600 units ≈ 6 uploads/day)
