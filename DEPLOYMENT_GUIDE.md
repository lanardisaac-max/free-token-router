# Deployment Guide — Free Token Router on Railway

**Estimated time: 5-10 minutes**

---

## Step 1: Prepare GitHub Repository

### Create repo on GitHub

```bash
# Navigate to your projects folder
cd ~/projects

# Clone/create the repo
git clone https://github.com/your-username/free-token-router.git
cd free-token-router

# Copy the app.py, requirements.txt, railway.json, .env.example, and README.md files
# (These are in the scratchpad)

# Initialize git
git add .
git commit -m "Initial commit: Free token router service"
git push -u origin main
```

---

## Step 2: Create Railway Project

### Option A: Via Railway CLI (Fastest)

```bash
# Install Railway CLI if not already installed
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project in the repo directory
cd free-token-router
railway init

# Follow prompts:
# - Project name: "free-token-router"
# - Environment: production
# - Connect to GitHub: Yes → Select your repo

# Deploy
railway up
```

**Done!** Your service is live. Railway will give you a URL like:
```
https://free-token-router-production.up.railway.app
```

### Option B: Via Railway Dashboard (Visual)

1. Go to https://railway.app
2. Click "Create Project" → "Deploy from GitHub"
3. Select `free-token-router` repo
4. Click "Deploy"
5. Wait 2-3 minutes for build to complete

---

## Step 3: Configure Environment Variables

### In Railway Dashboard

1. Go to your project
2. Click "Variables" tab
3. Add these environment variables:

```
ANTHROPIC_API_KEY = sk-ant-xxxxxxxxxxxxx
OPENAI_API_KEY = sk-xxxxxxxxxxxxx
COHERE_API_KEY = xxxxxxxxxxxxx
PORT = 8000
```

**Note:** Add at least ONE API key. More keys = better redundancy.

### Get API Keys

- **Claude:** https://console.anthropic.com/ (free $5 monthly credit)
- **OpenAI:** https://platform.openai.com/api-keys (free $5 trial)
- **Cohere:** https://dashboard.cohere.com/ (free tier available)

---

## Step 4: Verify Deployment

### Check Health Endpoint

```bash
curl https://free-token-router-production.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "available_providers": ["claude", "openai", "cohere"],
  "usage_stats": {"claude": 0, "openai": 0, "cohere": 0}
}
```

### Test Request

```bash
curl -X POST https://free-token-router-production.up.railway.app/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Say hello in one word"}]
  }'
```

**Expected response:** Message from Claude with "hello" or similar

---

## Step 5: Connect to Your Projects

### For FMC (FilterMyCall)

Update `FMC/.env`:
```
ANTHROPIC_API_BASE=https://free-token-router-production.up.railway.app/v1
```

Update code in FMC to use the base URL:
```python
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_API_BASE")
)
```

### For XOLVARA

Same as FMC (both use Anthropic).

### For CFP (CallerFilterPro)

Same as FMC.

### For All Projects

Create a shared `.env.routing` file:
```
LLM_ROUTER_BASE_URL=https://free-token-router-production.up.railway.app/v1
```

Then in each project's main config:
```python
os.getenv("LLM_ROUTER_BASE_URL", "https://api.anthropic.com/v1")
```

---

## Step 6: Monitor Usage

### Check Health Every Hour

```bash
watch -n 3600 'curl https://free-token-router-production.up.railway.app/health | jq'
```

### View Logs in Railway

1. Dashboard → "Deployments" tab
2. Click latest deployment
3. View logs in real-time

### Set Up Alerts

Monitor the `/health` endpoint. Alert if:
- Status changes to "unhealthy"
- All providers become unavailable

---

## Troubleshooting

### Deployment Fails

**Check logs:**
```bash
railway logs
```

**Common issues:**
- ❌ Missing `requirements.txt` → Add it
- ❌ Wrong Python version → Railway defaults to latest (OK)
- ❌ Missing API keys → Add to Variables tab

### Service Running But Requests Fail

**Check health:**
```bash
curl https://free-token-router-production.up.railway.app/health
```

**If unhealthy:**
- No providers available → Add API keys to Variables
- Provider down → Check API provider status page

### Slow Responses

**Check usage:**
```bash
curl https://free-token-router-production.up.railway.app/health | jq .usage_stats
```

If heavily skewed to one provider, that provider may be rate-limited. Add more keys.

---

## Costs

**This setup is FREE because:**
- ✅ Railway free tier: 500 RAM hours/month (more than enough for lightweight router)
- ✅ Claude free tier: $5 monthly credit
- ✅ OpenAI free tier: $5 trial credits
- ✅ Cohere free tier: 1000 requests/day

**Total: $0/month** (when used under free tier limits)

---

## Next Steps

1. ✅ Deploy router to Railway
2. ✅ Configure API keys
3. ✅ Test `/health` endpoint
4. ✅ Update all your projects to use `ANTHROPIC_API_BASE`
5. ✅ Monitor usage with `/health` checks

---

## Support

Need help?

1. Check `/health` endpoint
2. View Railway logs: `railway logs`
3. Test with curl to isolate issue
4. Check API provider status pages

---

**Deployed:** (URL assigned by Railway after Step 2)  
**Status:** Ready for production use
