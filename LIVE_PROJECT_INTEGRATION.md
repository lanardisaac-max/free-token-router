# Free Token Router — Live Project Integration

**Your router is LIVE:** `https://free-token-router-production.up.railway.app/v1`

Integrate this URL into each of your 10 live projects.

---

## 🚀 Router URL (Copy This)

```
https://free-token-router-production.up.railway.app/v1
```

**Keep this in your clipboard** — you'll need it for every project.

---

## 📋 Integration Steps (Per Project)

For **each project**, do these 2 things:

### Step 1: Add Environment Variable in Railway

1. Go to **railway.app** → Select your project
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   ```
   Name: LLM_ROUTER_BASE_URL
   Value: https://free-token-router-production.up.railway.app/v1
   ```
5. Click **"Save"** (auto-deploys)

### Step 2: Update Code in GitHub

Depends on your project type:

#### For Node.js/TypeScript Projects (FMC, CFP, HVACReception, etc.)

Find the Anthropic client initialization:

```javascript
// BEFORE:
const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

// AFTER:
const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
  baseURL: process.env.LLM_ROUTER_BASE_URL || "https://api.anthropic.com/v1",
})
```

#### For Python Projects (XOLVARA, Sanctuary, etc.)

Find the Anthropic client initialization:

```python
# BEFORE:
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# AFTER:
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("LLM_ROUTER_BASE_URL", "https://api.anthropic.com/v1")
)
```

**Then:** Create a PR, review, merge.

---

## ✅ Project Checklist

### 1. **FMC** (FilterMyCall)
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable
- [ ] GitHub: Update Anthropic client (Node.js)
- [ ] Create PR, review, merge

### 2. **XOLVARA**
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable
- [ ] GitHub: Update Anthropic client (Python)
- [ ] Create PR, review, merge

### 3. **CFP** (CallerFilterPro)
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable
- [ ] GitHub: Update Anthropic client (Node.js)
- [ ] Create PR, review, merge

### 4. **HVACReception**
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable
- [ ] GitHub: Update Anthropic client (Node.js)
- [ ] Create PR, review, merge

### 5. **Sanctuary**
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable
- [ ] GitHub: Update Anthropic client (Python)
- [ ] Create PR, review, merge

### 6. **SpamBlockReport**
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable (if uses Anthropic)
- [ ] GitHub: Update Anthropic client
- [ ] Create PR, review, merge

### 7. **StopRobocalls.AI**
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable (if uses Anthropic)
- [ ] GitHub: Update Anthropic client
- [ ] Create PR, review, merge

### 8. **ASCS** (Senior Services)
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable (if uses Anthropic)
- [ ] GitHub: Update Anthropic client
- [ ] Create PR, review, merge

### 9. **AIConciergePro**
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable (if uses Anthropic)
- [ ] GitHub: Update Anthropic client
- [ ] Create PR, review, merge

### 10. **AIServiceDeskPro**
- [ ] Railway: Add `LLM_ROUTER_BASE_URL` variable (if uses Anthropic)
- [ ] GitHub: Update Anthropic client
- [ ] Create PR, review, merge

---

## 🧪 Testing After Integration

Once you've updated a project:

1. **Deploy to Railway** (via GitHub merge or Railway dashboard)
2. **Trigger an LLM call** in the app
3. **Check the router health:**
   ```bash
   curl https://free-token-router-production.up.railway.app/health
   ```
4. **Look for increased `usage_stats`** — if Claude/OpenAI/Cohere count goes up, it's working! ✅

---

## 💡 Tips

- **Add router URL to Railway first** — this ensures fallback works even if code isn't updated yet
- **Update code in GitHub** — the `baseURL` parameter tells Anthropic SDK where to send requests
- **Include fallback** — the `||` ensures it falls back to official API if router is down
- **No code changes needed** for projects that don't use Anthropic SDK

---

## 📊 Expected Impact

**Before integration:**
- Each project: $20-50/month LLM costs
- Total: $200-500+/month

**After integration:**
- Each project: $0/month (free tier)
- Total: **$200-500+/month SAVED** 🎉
- Annual: **$2,400-6,000+ SAVED**

---

## 🔗 Your Router

- **URL:** https://free-token-router-production.up.railway.app
- **Health:** https://free-token-router-production.up.railway.app/health
- **API Base:** https://free-token-router-production.up.railway.app/v1

---

## 🆘 Troubleshooting

**Router not responding?**
- Check Railway project status (should be "Running")
- Verify API keys are added to Railway variables
- Check service logs in Railway dashboard

**Project still using direct API?**
- Verify `LLM_ROUTER_BASE_URL` is in Railway variables
- Verify code has `baseURL`/`base_url` parameter
- Redeploy from GitHub

**Slow requests?**
- All providers may be processing requests
- Check `/health` to see which providers are available
- Add more API keys to Railway router variables

---

**Ready to integrate? Start with FMC or CFP (simplest), then work through the rest!**

Router is live and waiting. Go get 'em! 🚀
