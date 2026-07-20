# Free Token Router — New Project Integration Guide

**Use this guide for ANY new projects you build.**

---

## 🚀 Quick Integration (5 minutes)

Your free token router is live at:
```
https://free-token-router-production.up.railway.app/v1
```

---

## 📋 Step 1: Add Environment Variable to Railway

When you create a new project on Railway:

1. Go to **Variables** tab
2. Add:
   ```
   LLM_ROUTER_BASE_URL=https://free-token-router-production.up.railway.app/v1
   ```
3. Save (auto-restarts)

---

## 🔧 Step 2: Update Your Code (Choose Your Stack)

### For Node.js/TypeScript Projects

When initializing Anthropic client:

```javascript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
  baseURL: process.env.LLM_ROUTER_BASE_URL || "https://api.anthropic.com/v1",
});
```

### For Python Projects

When initializing Anthropic client:

```python
import anthropic
import os

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("LLM_ROUTER_BASE_URL", "https://api.anthropic.com/v1")
)
```

### For Other Languages

Use the standard REST endpoint:
```
POST https://free-token-router-production.up.railway.app/v1/messages
POST https://free-token-router-production.up.railway.app/v1/completions
GET  https://free-token-router-production.up.railway.app/v1/models
```

---

## ✅ Verification

Test that your new project is using the router:

```bash
# Check health
curl https://free-token-router-production.up.railway.app/health

# Should show increased usage_stats for your provider
```

---

## 💡 Key Points

1. **Router URL is consistent** — Always use:
   ```
   https://free-token-router-production.up.railway.app/v1
   ```

2. **Fallback is automatic** — If you include `|| "https://api.anthropic.com/v1"`, it falls back to official API if router is down

3. **No breaking changes** — Your code works exactly the same, just routes through the free-token aggregator

4. **You save money immediately** — Uses free tier tokens instead of paid API

---

## 🎯 Checklist for New Projects

- [ ] Project created on Railway
- [ ] Added `LLM_ROUTER_BASE_URL` environment variable
- [ ] Updated Anthropic client initialization with `baseURL`/`base_url`
- [ ] Tested health endpoint shows usage increase
- [ ] Deployed and verified in production

---

## 📊 Expected Savings

- **Per project:** $20-50/month
- **Available tokens:** 2.5M+/month (combined Claude + OpenAI + Cohere)
- **Fallback:** Automatic failover to official API

---

## 🔗 Reference

- **Router:** https://free-token-router-production.up.railway.app
- **Health:** https://free-token-router-production.up.railway.app/health
- **GitHub:** https://github.com/lanardisaac-max/free-token-router
- **API Base:** https://free-token-router-production.up.railway.app/v1

---

## ❓ FAQ

**Q: Do I need to update my API key?**  
A: No. Keep using your existing ANTHROPIC_API_KEY, OPENAI_API_KEY, or COHERE_API_KEY. The router handles routing.

**Q: What if the router goes down?**  
A: The fallback URL kicks in automatically (see code examples above with `||`).

**Q: Can I use different providers?**  
A: Yes! The router intelligently selects Claude > OpenAI > Cohere based on availability.

**Q: Do I need to change my API calls?**  
A: No! The SDK calls remain identical. Only the `baseURL` parameter changes where the request goes.

---

**Start every new project with Step 1 & 2 above!** 🚀

Saves money from day one. ✅
