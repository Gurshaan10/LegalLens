# Railway Deployment Guide for Legal Lens

## Project Created!
**Railway Project URL:** https://railway.com/project/090ce236-bff4-4f51-92ea-3540433928bb

---

## Step 1: Add PostgreSQL Database

1. Go to your Railway project dashboard (link above)
2. Click the **"+ New"** button
3. Select **"Database"** → **"Add PostgreSQL"**
4. Railway will automatically:
   - Provision a PostgreSQL database
   - Set the `DATABASE_URL` environment variable
   - Link it to your service

---

## Step 2: Set Environment Variables

1. In Railway dashboard, click on your service
2. Go to the **"Variables"** tab
3. Add these variables:

### Required Variables:

```
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### Firebase Admin SDK:
You need to paste the **entire contents** of `backend/firebase-admin.json` as a **single-line JSON string**.

Option A - Single line format:
```
FIREBASE_ADMIN_CREDENTIAL={"type":"service_account","project_id":"legal-lens-f1e3d",...entire JSON...}
```

Option B - Keep as file (recommended):
Railway doesn't support file uploads via CLI, so you'll need to:
1. Convert firebase-admin.json to base64: `base64 backend/firebase-admin.json`
2. Add as env var: `FIREBASE_ADMIN_CREDENTIAL_BASE64=<base64-string>`
3. Update backend code to decode it

**Easier approach:** Use the JSON directly as shown in Option A.

### Optional Variables (defaults are fine):
```
HOST=0.0.0.0
PORT=$PORT
```

---

## Step 3: Deploy Backend

From your terminal, run:

```bash
cd /Users/gurshaansingh/Desktop/Legal_Lens
railway up
```

This will:
- Upload your code
- Install dependencies from `backend/requirements.txt`
- Run the start command from `railway.toml`
- Deploy your backend API

Railway will provide you with a URL like: `https://legal-lens-production.up.railway.app`

---

## Step 4: Verify Deployment

Once deployed, test your backend:

```bash
# Get your Railway URL
railway domain

# Test health endpoint
curl https://your-app.up.railway.app/health
```

You should see: `{"status":"healthy"}`

---

## Step 5: Deploy Frontend (Vercel)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy frontend:
```bash
cd frontend
vercel
```

3. Follow prompts:
   - Project name: `legal-lens-frontend`
   - Framework: `Vite`
   - Build command: `npm run build`
   - Output directory: `dist`

4. Set environment variable on Vercel:
   - Go to Vercel dashboard → Your project → Settings → Environment Variables
   - Add: `VITE_API_BASE_URL` = `https://your-railway-url.up.railway.app`

5. Redeploy to apply env var:
```bash
vercel --prod
```

---

## Step 6: Update CORS

After getting your Vercel frontend URL, update Railway backend:

1. Go to Railway dashboard → Variables tab
2. Update `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

Or update in backend/main.py CORS middleware to include your Vercel URL.

---

## Step 7: Test Live App!

1. Visit your Vercel frontend URL
2. Try the demo document
3. Upload a PDF
4. Ask questions

---

## Troubleshooting

### Check Logs:
```bash
railway logs
```

### Common Issues:

**1. Database Connection Error:**
- Verify DATABASE_URL is set automatically by Railway
- Check PostgreSQL addon is running

**2. OpenAI API Error:**
- Verify OPENAI_API_KEY is set correctly
- Check your OpenAI account has credits

**3. Firebase Auth Error:**
- Verify FIREBASE_ADMIN_CREDENTIAL JSON is valid
- Check Firebase project settings

**4. Import Errors:**
- Railway should install all requirements.txt dependencies
- Check logs for missing packages

---

## Quick Commands Reference

```bash
# View logs
railway logs

# Open Railway dashboard
railway open

# Get deployment URL
railway domain

# Redeploy
railway up

# Check service status
railway status
```

---

## Cost Estimate (Railway Free Tier)

- **Backend:** Uses execution time (~500 hours/month free)
- **PostgreSQL:** Free with limitations (500MB storage, 5GB transfer)
- **Frontend (Vercel):** Completely free for hobby projects

**Total Cost: $0/month** (within free tier limits)

---

## Next: Make it Production-Ready

1. Add custom domain (optional)
2. Set up monitoring (Railway Metrics)
3. Configure auto-deploy from GitHub
4. Add database backups
5. Set up staging environment
