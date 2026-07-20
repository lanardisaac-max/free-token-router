# 🚀 Deploy to Railway NOW — Step-by-Step

**Your code is ready. Follow these steps to go live in 10 minutes.**

---

## ✅ What's Already Done

- ✅ Code pushed to GitHub: https://github.com/lanardisaac-max/free-token-router
- ✅ All dependencies listed in `requirements.txt`
- ✅ Railway config ready in `railway.json`
- ✅ Environment template in `.env.example`

**Status:** READY FOR DEPLOYMENT

---

## 🎯 Deploy via Railway Dashboard (Easiest)

Since you're already logged into Railway, use the dashboard:

### Step 1: Go to Railway Dashboard

1. Open: https://railway.app/dashboard
2. You should see your projects (you're already logged in)

### Step 2: Create New Project

1. Click **"Create Project"** button (top-right)
2. Select **"Deploy from GitHub"**
3. Select the repo: **`free-token-router`**
4. Click **"Deploy"**

**⏳ Wait 2-3 minutes for build to complete**

### Step 3: Get Your URL

Once deployment finishes:
1. Click on the **`free-token-router`** project
2. Look for the **"Production"** service
3. Click it to expand
4. Find the **public URL** (looks like: `https://free-token-router-production.up.railway.app`)

**💾 Copy this URL — you'll need it for all projects**

### Step 4: Add Environment Variables

1. In Railway project, click **"Variables"** tab
2. Click **"Add Variable"** for each:

#### Variable 1: ANTHROPIC_API_KEY
```
Name: ANTHROPIC_API_KEY
Value: sk-ant-[your key from console.anthropic.com]
```

#### Variable 2: OPENAI_API_KEY
```
Name: OPENAI_API_KEY
Value: sk-[your key from platform.openai.com]
```

#### Variable 3: COHERE_API_KEY
```
Name: COHERE_API_KEY
Value: [your key from dashboard.cohere.com]
```

**Note:** At least ONE key required. More keys = better redundancy.

3. Click **"Deploy"** or wait for auto-restart (30 seconds)

---

## ✅ Test Deployment

Once deployed, test these endpoints:

### Health Check (tells you which providers are active)
```bash
curl https://free-token-router-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "available_providers": ["claude", "openai", "cohere"],
  "usage_stats": {"claude": 0, "openai": 0, "cohere": 0}
}
```

### Test API Request
```bash
curl -X POST https://free-token-router-production.up.railway.app/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Say hello in one word"}]
  }'
```

Expected: Claude responds with a message

---

## 📋 Deployment Checklist

- [ ] Created project in Railway dashboard
- [ ] Selected `free-token-router` repo
- [ ] Deployment completed (no red errors)
- [ ] Copied the production URL
- [ ] Added ANTHROPIC_API_KEY
- [ ] Added OPENAI_API_KEY (optional but recommended)
- [ ] Added COHERE_API_KEY (optional but recommended)
- [ ] Health check returns "healthy"
- [ ] API test returns a message

---

## 🚨 If Deployment Fails

### Build error?
1. Check Railway Logs tab
2. Most common: missing Python dependencies
3. Solution: All are in `requirements.txt` — already set

### Runtime error?
1. Check Logs tab
2. Look for traceback
3. Most common: Missing API key
4. Solution: Add at least one key to Variables

### Health check fails?
1. Check if service is running (should show "Running" in Railway)
2. Wait 30 seconds after deploy
3. Check URL is correct (no typos)

---

## 🔗 Your Deployment URL

Once deployed, your URL will be:
```
https://free-token-router-production.up.railway.app
```

**Save this! Use everywhere below.**

---

## 🎉 Next Steps

Once deployed, integrate with your projects:

### Quick Start (5 minutes)
```bash
cd ~/projects/fmc
echo "LLM_ROUTER_BASE_URL=https://free-token-router-production.up.railway.app/v1" >> .env
# Update Anthropic client to use baseURL parameter
npm run dev
```

### Full Integration (per project)
See `PROJECT_INTEGRATION_GUIDE.md` for detailed steps.

---

## 📞 Support

**Status page:** https://www.railwaystatus.com  
**Logs:** Railway dashboard → Project → Logs tab  
**Health:** `curl .../health` should show "healthy"

---

**Your router is production-ready. Deploy now!** 🚀
