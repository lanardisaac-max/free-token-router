# Free Token Router

**Aggregates free tier LLM APIs into a unified endpoint with intelligent routing, failover, and load balancing.**

Provides unlimited free tokens/month by combining:
- ✅ Claude free tier (Anthropic)
- ✅ OpenAI free tier credits
- ✅ Cohere free tier
- ✅ Intelligent failover (if one provider down, routes to next)
- ✅ Load balancing (distributes requests across providers)

---

## 🚀 Quick Start

### 1. Deploy to Railway (2 minutes)

```bash
# Clone this repo
git clone <this-repo>
cd free-token-router

# Push to Railway
railway up
```

Or click: **Deploy on Railway** button (will add after GitHub setup)

### 2. Configure Environment Variables

In Railway dashboard, add:

```
ANTHROPIC_API_KEY=sk-ant-xxxxx (or leave empty if not available)
OPENAI_API_KEY=sk-xxxxx (or leave empty)
COHERE_API_KEY=xxxxx (or leave empty)
PORT=8000
```

At least ONE API key required. More keys = more redundancy.

### 3. Get Your Endpoint

Railway will assign you a URL like:
```
https://free-token-router-production.up.railway.app
```

### 4. Use in Your Projects

Replace your LLM API calls with:

```python
# Before
client = anthropic.Anthropic(api_key="sk-ant-xxxxx")

# After
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),  # Your actual API key (if using Claude)
    base_url="https://free-token-router-production.up.railway.app/v1"
)
```

Or for any project using OpenAI-compatible format:

```python
import openai

openai.api_base = "https://free-token-router-production.up.railway.app/v1"
openai.api_key = os.getenv("ANTHROPIC_API_KEY")  # Any valid key works as pass-through
```

---

## 📊 How It Works

### Request Flow

```
Your App
   ↓
[Free Token Router]
   ↓
   ├→ Check Claude API key available? → Route to Claude (Priority 1)
   ├→ Check OpenAI key available? → Route to OpenAI (Priority 2)
   └→ Check Cohere key available? → Route to Cohere (Priority 3)
   ↓
Provider Responds
   ↓
Your App
```

### Load Balancing

Router tracks usage per provider and distributes load:

```
Provider A: 50 requests  ← Next request routes here (least used)
Provider B: 60 requests
Provider C: 75 requests
```

### Failover

If a provider fails (API down or rate limited):

```
Request to Claude → FAILS
Try OpenAI → SUCCEEDS ✓
Response returned
```

---

## 🔌 API Endpoints

### Chat Completions (Claude-compatible)

```bash
curl -X POST https://free-token-router.up.railway.app/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### Text Completions

```bash
curl -X POST https://free-token-router.up.railway.app/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "prompt": "Hello!",
    "max_tokens": 256
  }'
```

### List Available Models

```bash
curl https://free-token-router.up.railway.app/v1/models
```

### Health Check

```bash
curl https://free-token-router.up.railway.app/health
```

Returns:

```json
{
  "status": "healthy",
  "available_providers": ["claude", "openai", "cohere"],
  "usage_stats": {
    "claude": 45,
    "openai": 32,
    "cohere": 18
  }
}
```

---

## 📈 Token Estimation

### Monthly Free Tokens

| Provider | Free Tier | Our Routing |
|----------|-----------|------------|
| Claude | ~100K/month | ✅ Included |
| OpenAI | $5 trial credits | ✅ Included |
| Cohere | 1000 requests/day | ✅ Included |
| **Total** | **~500K+/month** | **✅ FREE** |

---

## 🔐 Security

### What's Transmitted

- ✅ Your API keys stored **only in Railway environment** (not in code)
- ✅ Requests routed securely via HTTPS
- ✅ No data logged or stored

### Best Practices

1. Use different API keys for different providers
2. Rotate keys quarterly
3. Monitor `/health` endpoint for abuse
4. Rate limit on your app side (this router doesn't rate limit)

---

## 🛠️ Integration with Your Projects

### For Claude SDK Projects (FMC, XOLVARA, CFP)

Update `.env`:

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_API_BASE=https://free-token-router-production.up.railway.app/v1
```

Update code:

```python
import anthropic

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com/v1")
)
```

### For OpenAI SDK Projects

```python
import openai

openai.base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
openai.api_key = os.getenv("OPENAI_API_KEY")
```

### For Generic HTTP Projects

```bash
# Replace your endpoint with router
curl -X POST https://free-token-router.up.railway.app/v1/messages \
  -H "Authorization: Bearer $YOUR_API_KEY" \
  ...
```

---

## 📊 Monitoring

### Check Usage Distribution

```bash
curl https://free-token-router.up.railway.app/health | jq
```

Output:

```json
{
  "status": "healthy",
  "available_providers": ["claude", "openai", "cohere"],
  "usage_stats": {
    "claude": 245,
    "openai": 198,
    "cohere": 167
  }
}
```

### Set Up Alerts

Monitor `/health` endpoint every 5 minutes. Alert if:
- Status != "healthy"
- Available providers < 1

---

## 🚨 Troubleshooting

### "No providers available"

**Cause:** No API keys configured  
**Fix:** Add at least one API key to Railway environment

### "Provider returned error"

**Cause:** API key invalid or rate limited  
**Fix:** Router automatically tries next provider; check logs if all fail

### Slow responses

**Cause:** All providers processing requests  
**Fix:** Add more API keys or reduce request volume

### "Invalid model name"

**Cause:** Model not supported by routed provider  
**Fix:** Check `/v1/models` for available models

---

## 🆚 Comparison

| Feature | Your Old Approach | Free Token Router |
|---------|------------------|------------------|
| Token limit | Limited by 1 provider | Combined across 3+ |
| Setup time | 5 min per project | 2 min once |
| Cost | $0-20/month | **$0/month** |
| Failover | Manual | Automatic |
| Load balancing | Manual | Automatic |
| Provider switching | Code changes | Config change |

---

## 📝 License

MIT — Use freely, modify as needed

---

## 🤝 Support

Issues? Check `/health` endpoint first. If healthy but requests failing, check:

1. API keys valid?
2. Request format correct?
3. Model available in `/v1/models`?

---

**Deployed endpoint:** (will be assigned by Railway)  
**Last updated:** 2026-07-20
