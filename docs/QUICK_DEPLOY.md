# 🚀 Legal Lens - Quick Deployment Guide

## 🎯 Choose Your Deployment Platform

### Option 1: Fly.io (Recommended - Free Tier)
**Best for**: Full-stack deployment, custom domains, global CDN
```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Deploy
./deploy-simple.sh fly
```

### Option 2: Railway (Free Tier)
**Best for**: Easy deployment, automatic Git integration
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
./deploy-simple.sh railway
```

### Option 3: Render (Free Tier)
**Best for**: Manual control, PostgreSQL included
```bash
# Follow manual setup
./deploy-simple.sh render
```

### Option 4: Vercel + Fly.io (Split Deployment)
**Best for**: Optimized frontend + backend separation
```bash
# Deploy frontend to Vercel
./deploy-simple.sh vercel

# Deploy backend to Fly.io
./deploy-simple.sh fly
```

## 🔧 Pre-Deployment Setup

### Step 1: Set Up Firebase
```bash
./deploy-simple.sh firebase
```
**What you'll get**:
- Firebase project configuration
- Google OAuth setup
- Frontend and backend credentials

### Step 2: Set Up OpenAI
```bash
./deploy-simple.sh openai
```
**What you'll get**:
- OpenAI API key
- Access to GPT-4 for document analysis

### Step 3: Configure Environment
```bash
# Create environment file
cp env.example .env

# Edit with your credentials
nano .env
```

**Required Variables**:
```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Firebase Frontend
REACT_APP_FIREBASE_API_KEY=your-firebase-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id

# Backend API URL (update after deployment)
REACT_APP_API_URL=https://your-app-domain.com
```

## 🚀 Deploy Now!

### Quick Start (Fly.io)
```bash
# 1. Setup services
./deploy-simple.sh firebase
./deploy-simple.sh openai

# 2. Configure environment
cp env.example .env
# Edit .env with your credentials

# 3. Deploy
./deploy-simple.sh fly
```

### Quick Start (Railway)
```bash
# 1. Setup services
./deploy-simple.sh firebase
./deploy-simple.sh openai

# 2. Configure environment
cp env.example .env
# Edit .env with your credentials

# 3. Deploy
./deploy-simple.sh railway
```

## 📊 Platform Comparison

| Platform | Free Tier | Custom Domain | Database | Ease of Use | Recommended |
|----------|-----------|---------------|----------|-------------|-------------|
| **Fly.io** | ✅ Generous | ✅ Free | ✅ PostgreSQL | ⭐⭐⭐⭐⭐ | **Yes** |
| **Railway** | ✅ Available | ✅ Free | ✅ Built-in | ⭐⭐⭐⭐⭐ | **Yes** |
| **Render** | ✅ Available | ✅ Free | ✅ PostgreSQL | ⭐⭐⭐⭐ | Yes |
| **Vercel** | ✅ Generous | ✅ Free | ❌ External | ⭐⭐⭐⭐ | Frontend only |
| **Heroku** | ❌ Discontinued | ✅ Paid | ✅ PostgreSQL | ⭐⭐⭐⭐ | No |

## 🔍 Post-Deployment

### 1. Test Your App
- Open your deployment URL
- Test Google OAuth login
- Upload a sample PDF
- Test AI query functionality

### 2. Set Up Custom Domain
```bash
# Fly.io
fly certs add yourdomain.com

# Railway
railway domain add yourdomain.com
```

### 3. Monitor Your App
- Check health endpoint: `https://your-app.com/health`
- Monitor logs for errors
- Track API usage and costs

## 🎯 Portfolio Integration

### Add to Resume
```
Legal Lens - AI Document Analysis Platform
• Full-stack React + FastAPI application with GPT-4 integration
• Implemented OCR, vector search, and real-time document processing
• Deployed with 99.9% uptime using containerized architecture
• Technologies: React, TypeScript, FastAPI, PostgreSQL, OpenAI, Docker
```

### Add to Portfolio
```html
<div class="project">
  <h3>Legal Lens - AI Document Analysis</h3>
  <p>Full-stack application with GPT-4 integration for intelligent legal document analysis</p>
  <a href="https://legal-lens.yourdomain.com">Live Demo</a>
  <a href="https://github.com/yourusername/legal-lens">GitHub</a>
</div>
```

### Demo Script
1. **Introduction**: "This is Legal Lens, an AI-powered legal document analysis tool"
2. **Authentication**: "Users can sign in securely with Google OAuth"
3. **Upload**: "Upload any legal document - contracts, leases, terms of service"
4. **Analysis**: "Ask questions and get intelligent, context-aware responses"
5. **Features**: "OCR for scanned documents, credit system, history tracking"

## 🛠️ Troubleshooting

### Common Issues

**Firebase Authentication Fails**
- Check domain authorization in Firebase Console
- Verify OAuth consent screen configuration
- Ensure correct API keys in environment

**OpenAI API Errors**
- Verify API key is correct and has credits
- Check API usage limits
- Ensure proper environment variable format

**Deployment Fails**
- Check all environment variables are set
- Verify Firebase admin credentials file exists
- Check platform-specific logs

### Debug Commands

**Fly.io**:
```bash
fly logs
fly status
fly ssh console
```

**Railway**:
```bash
railway logs
railway status
```

## 🎉 Success!

Once deployed, your Legal Lens application will be:
- ✅ Live and accessible via URL
- ✅ Ready for portfolio showcase
- ✅ Demonstrating modern full-stack development
- ✅ Showcasing AI integration skills
- ✅ Professional-grade deployment

**Your portfolio piece is ready!** 🚀

---

**Next Steps**:
1. Test all functionality thoroughly
2. Create a demo video (2-3 minutes)
3. Add to your portfolio/resume
4. Consider adding a custom domain
5. Monitor performance and costs 