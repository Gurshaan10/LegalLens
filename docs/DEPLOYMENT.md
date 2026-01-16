# Legal Lens Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Fly.io (Recommended - Free Tier)
```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login to Fly
fly auth login

# 3. Deploy
./deploy.sh fly
```

### Option 2: Railway (Free Tier)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Deploy
./deploy.sh railway
```

### Option 3: Local Docker
```bash
# Deploy locally
./deploy.sh local
```

## 🔧 Pre-Deployment Setup

### 1. Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy the example file
cp env.example .env

# Edit with your actual values
nano .env
```

**Required Variables**:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Firebase Configuration (Backend)
FIREBASE_ADMIN_CREDENTIAL=firebase-admin.json

# Firebase Configuration (Frontend)
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id

# Backend API URL (for production)
REACT_APP_API_URL=https://your-app-domain.com
```

### 2. Firebase Setup

1. **Create Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project
   - Enable Google Authentication

2. **Get Frontend Config**:
   - Go to Project Settings > General
   - Scroll down to "Your apps"
   - Add a web app
   - Copy the configuration

3. **Get Backend Credentials**:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save as `backend/firebase-admin.json`

### 3. OpenAI Setup

1. **Get API Key**:
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create an account or sign in
   - Go to API Keys section
   - Create a new API key

2. **Add to Environment**:
   - Add the API key to your `.env` file

## 🌐 Platform-Specific Deployment

### Fly.io Deployment

**Advantages**:
- Free tier with generous limits
- Global CDN
- Automatic HTTPS
- Easy scaling

**Steps**:
```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Create app (first time only)
fly apps create legal-lens

# 4. Set secrets
fly secrets set OPENAI_API_KEY="your_key_here"
fly secrets set FIREBASE_ADMIN_CREDENTIAL="firebase-admin.json"

# 5. Deploy
fly deploy

# 6. Open app
fly open
```

**Custom Domain**:
```bash
# Add custom domain
fly certs add yourdomain.com

# Update DNS records as instructed
```

### Railway Deployment

**Advantages**:
- Free tier available
- Automatic deployments from Git
- Built-in database
- Easy environment management

**Steps**:
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Set environment variables
railway variables set OPENAI_API_KEY="your_key_here"

# 5. Deploy
railway up

# 6. Get URL
railway domain
```

### Heroku Deployment

**Note**: Heroku discontinued their free tier, but paid plans are available.

**Steps**:
```bash
# 1. Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create legal-lens

# 4. Set environment variables
heroku config:set OPENAI_API_KEY="your_key_here"

# 5. Deploy
git push heroku main

# 6. Open app
heroku open
```

## 🔍 Post-Deployment Verification

### 1. Health Check
```bash
# Test health endpoint
curl https://your-app-domain.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

### 2. Frontend Test
- Open your app URL
- Test Google OAuth login
- Upload a sample PDF
- Test AI query functionality

### 3. Backend API Test
```bash
# Test API endpoints
curl -X GET https://your-app-domain.com/me \
  -H "Authorization: Bearer your_token_here"
```

## 🛠️ Troubleshooting

### Common Issues

**1. Environment Variables Not Set**
```bash
# Check if variables are set
fly secrets list
railway variables
heroku config
```

**2. Firebase Authentication Issues**
- Verify Firebase project settings
- Check OAuth consent screen
- Ensure correct domain is authorized

**3. OpenAI API Errors**
- Verify API key is correct
- Check API usage limits
- Ensure sufficient credits

**4. Database Connection Issues**
- Check database URL format
- Verify database is accessible
- Check connection pooling settings

### Debug Commands

**Fly.io**:
```bash
# View logs
fly logs

# SSH into app
fly ssh console

# Check app status
fly status
```

**Railway**:
```bash
# View logs
railway logs

# Check status
railway status
```

**Heroku**:
```bash
# View logs
heroku logs --tail

# Check app status
heroku ps
```

## 📊 Monitoring & Maintenance

### Health Monitoring
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Configure error tracking (Sentry)
- Monitor API usage and costs

### Performance Optimization
- Enable CDN for static assets
- Implement caching strategies
- Monitor database performance
- Optimize image processing

### Security Updates
- Keep dependencies updated
- Monitor security advisories
- Regular security audits
- Update API keys periodically

## 🎯 Portfolio Integration

### Custom Domain Setup
1. **Purchase Domain**: Use Namecheap, GoDaddy, or similar
2. **Configure DNS**: Point to your deployed app
3. **SSL Certificate**: Most platforms provide automatic SSL
4. **Update Portfolio**: Add live link to your resume/portfolio

### Demo Video Creation
1. **Record Screen**: Use Loom, OBS, or similar
2. **Show Key Features**: Authentication, upload, AI analysis
3. **Keep it Short**: 2-3 minutes maximum
4. **Professional Quality**: Good audio, clear visuals

### Portfolio Page Integration
```html
<!-- Example portfolio section -->
<div class="project">
  <h3>Legal Lens - AI Document Analysis</h3>
  <p>Full-stack application with GPT-4 integration for legal document analysis</p>
  <a href="https://legal-lens.yourdomain.com">Live Demo</a>
  <a href="https://github.com/yourusername/legal-lens">GitHub</a>
</div>
```

## 🚀 Next Steps

### Immediate Actions
1. **Deploy to chosen platform**
2. **Set up custom domain**
3. **Create demo video**
4. **Update portfolio/resume**

### Future Enhancements
1. **Add monitoring and analytics**
2. **Implement advanced features**
3. **Scale for higher traffic**
4. **Consider monetization options**

---

**Your Legal Lens application is now ready for portfolio showcase!** 🎉 