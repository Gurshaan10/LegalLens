# Vercel Frontend Deployment Guide

## Quick Deploy to Vercel

### Step 1: Import Project

1. Go to: https://vercel.com/new
2. Click "Add New" → "Project"
3. Select "Import Git Repository"
4. Choose: **Gurshaan10/LegalLens**
5. Click "Import"

### Step 2: Configure Project Settings

**Framework Preset:** Vite
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `dist`
**Install Command:** `npm install`

### Step 3: Add Environment Variables

Click "Environment Variables" tab and add these:

#### Required Environment Variables:

```bash
# Backend API URL (Railway)
VITE_API_BASE_URL=https://legallens-production.up.railway.app

# Firebase Configuration (get from Firebase Console)
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=legal-lens-f1e3d.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=legal-lens-f1e3d
VITE_FIREBASE_STORAGE_BUCKET=legal-lens-f1e3d.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
VITE_FIREBASE_APP_ID=your_app_id_here
```

#### Where to find Firebase values:

1. Go to: https://console.firebase.google.com
2. Select project: **legal-lens-f1e3d**
3. Click gear icon → Project Settings
4. Scroll to "Your apps" → Web app
5. Copy the config values (apiKey, authDomain, etc.)

### Step 4: Deploy

1. Click "Deploy"
2. Wait 2-3 minutes for build to complete
3. Your frontend will be live at: `https://your-project.vercel.app`

### Step 5: Update Railway CORS

After deployment, update your Railway backend:

1. Go to: https://railway.com/project/090ce236-bff4-4f51-92ea-3540433928bb
2. Click on your backend service
3. Go to "Variables" tab
4. Add or update:
   ```
   ALLOWED_ORIGINS=https://your-vercel-url.vercel.app
   ```
5. Redeploy the backend service

---

## Troubleshooting

### Build Fails

**Error: "Cannot find module '@types/node'"**
- Solution: This should be in devDependencies, check package.json

**Error: "VITE_API_BASE_URL is undefined"**
- Solution: Make sure you added all environment variables in Vercel dashboard

### Frontend Deployed but API Calls Fail

**CORS Error:**
- Update Railway ALLOWED_ORIGINS (see Step 5 above)

**API returns 502/503:**
- Check Railway backend is running
- Verify DATABASE_URL is set in Railway
- Check Railway logs for errors

### Authentication Not Working

**Firebase Auth Fails:**
- Verify all VITE_FIREBASE_* variables are set correctly
- Check Firebase Console for authorized domains
- Add your Vercel domain to Firebase authorized domains

---

## Post-Deployment Checklist

- [ ] Frontend deploys successfully
- [ ] Backend API is accessible (test /health endpoint)
- [ ] Demo document loads
- [ ] Can query demo document
- [ ] Guest upload works (2/day limit)
- [ ] Google OAuth login works
- [ ] Registered user can upload with credits
- [ ] Account menu shows credits correctly
- [ ] Sign out works

---

## Your Deployment URLs

**Backend (Railway):** https://legallens-production.up.railway.app
**Frontend (Vercel):** _[Will be provided after deployment]_

**Test Backend Health:**
```bash
curl https://legallens-production.up.railway.app/health
```

Expected response:
```json
{"status":"healthy"}
```

**Test Demo Document:**
```bash
curl https://legallens-production.up.railway.app/demo
```

Expected: JSON with demo document info
