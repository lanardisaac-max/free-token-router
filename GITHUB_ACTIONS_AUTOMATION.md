# GitHub Actions Automation — Zero-Manual Integration for 50+ Sites

**Automatically integrate free token router into ALL your projects with zero manual work.**

---

## 🚀 How It Works

### Trigger: Every Git Push
When you push code to any of your project repos, GitHub Actions automatically:
1. ✅ Detects project type (Node.js or Python)
2. ✅ Checks for Anthropic SDK usage
3. ✅ Integrates router (updates code + env vars)
4. ✅ Creates PR for review
5. ✅ Reports savings

**Result:** Every project uses free tokens automatically.

---

## 📋 Setup (One-Time)

### For Each of Your 50+ Project Repos:

1. **Create the workflows directory** (if not exists):
   ```bash
   mkdir -p .github/workflows
   ```

2. **Copy one of two workflows:**

   **Option A: Auto on every push (Recommended)**
   ```bash
   # Copy this file to your project repo
   cp auto-integrate-router.yml .github/workflows/
   ```

   **Option B: Call from your CI pipeline**
   ```bash
   # Reference the reusable workflow
   # See example below
   ```

3. **Commit and push**
   ```bash
   git add .github/workflows/
   git commit -m "ci: add free token router auto-integration"
   git push
   ```

4. **Done!** Next push will trigger integration

---

## 🔧 Workflow Options

### Option 1: Standalone Workflow (Easiest)

Use this for projects that don't have CI/CD yet.

**File:** `.github/workflows/auto-integrate-router.yml`

**Trigger:** Automatically on every push  
**Action:** Creates PR with integration  
**Best for:** Simple projects, new projects

### Option 2: Reusable Workflow (Enterprise)

Use this if you already have CI/CD and want to integrate router into it.

**File:** `.github/workflows/reusable-router-setup.yml`

**Trigger:** Called from your existing workflows  
**Action:** Integrates router as part of your CI  
**Best for:** Monorepos, complex CI pipelines

---

## 📝 Example: Call Reusable Workflow

In your project's `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  setup-router:
    uses: lanardisaac-max/free-token-router/.github/workflows/reusable-router-setup.yml@master
    with:
      router_url: 'https://free-token-router-production.up.railway.app/v1'
      create_pr: true

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install && npm run build
```

---

## 🎯 What Gets Automated

### Automatically Detects:
- ✅ Node.js projects (package.json)
- ✅ Python projects (requirements.txt, pyproject.toml)
- ✅ Anthropic SDK usage (new Anthropic, anthropic.Anthropic)
- ✅ Existing router integration (skips if already done)

### Automatically Updates:
- ✅ Anthropic client initialization (adds baseURL/base_url)
- ✅ .env file (adds LLM_ROUTER_BASE_URL)
- ✅ Git commit (feat: integrate free token router)
- ✅ Creates PR (for review before merge)

### Automatically Reports:
- ✅ Which files were updated
- ✅ Router endpoint configured
- ✅ Estimated monthly savings ($20-50)
- ✅ Available free tokens (2.5M+)

---

## 💡 Real-World Examples

### Scenario 1: New Project Created
1. Developer pushes code to new repo
2. GitHub Actions detects it's a Node.js project
3. Finds Anthropic SDK usage
4. Auto-updates code + .env
5. Creates PR "feat: integrate free token router"
6. PR merged → $50/month savings enabled
7. **Zero manual work**

### Scenario 2: Existing Project
1. You add router workflow to existing repo
2. Next push triggers it
3. Auto-integrates router
4. Creates PR
5. **Same result, zero manual work**

### Scenario 3: 50 Projects (Batch)
1. Add workflow to all 50 repos simultaneously
2. Push to each repo (or use git script)
3. GitHub Actions runs on all 50
4. 50 PRs created automatically
5. Review and merge all 50
6. **$2,500/month in savings enabled instantly**

---

## 🛠️ Scaling to 50+ Sites

### Batch Setup Script

To add the workflow to multiple repos at once:

```bash
#!/bin/bash
# add-router-workflow.sh

REPOS=(
  "repo1"
  "repo2"
  "repo3"
  # ... add all 50 repo names
)

for repo in "${REPOS[@]}"; do
  echo "Setting up: $repo"
  cd "/path/to/$repo"
  
  # Download and add workflow
  mkdir -p .github/workflows
  curl -s https://raw.githubusercontent.com/lanardisaac-max/free-token-router/master/.github/workflows/auto-integrate-router.yml \
    -o .github/workflows/auto-integrate-router.yml
  
  # Commit and push
  git add .github/workflows/
  git commit -m "ci: add free token router auto-integration" || true
  git push
  
  echo "✓ $repo setup complete"
done
```

**Run it:**
```bash
bash add-router-workflow.sh
```

**Result:** All 50 repos have workflow + auto-integration starts immediately.

---

## 📊 Monitoring

### GitHub Actions Tab

After setup, each repo shows:
- ✅ Workflow runs (one per push)
- ✅ PR creation status
- ✅ Integration logs
- ✅ Failures (if any)

### Example Output:

```
✓ auto-integrate-router workflow passed
  ✓ Checkout code
  ✓ Detect project type: nodejs
  ✓ Check for Anthropic usage: Found
  ✓ Run integration: Success
  ✓ Create Pull Request: PR-1234 created
```

---

## 🔄 How It Prevents Double-Integration

The workflow is **idempotent** — it can run multiple times safely:

1. **First run:** Adds router integration → Creates PR
2. **Second run:** Detects `baseURL` already present → Skips → No duplicate PR
3. **Nth run:** Same behavior → Safe to run repeatedly

**You can safely:**
- Push multiple times
- Run workflow multiple times
- Integrate same repo multiple times
- Result: No duplicate changes, no duplicate PRs

---

## 🚨 Troubleshooting

### Workflow Doesn't Run
**Problem:** Workflow file doesn't trigger  
**Solution:** 
```bash
git add .github/workflows/auto-integrate-router.yml
git commit -m "add workflow"
git push  # This push should trigger the workflow
```

### No PR Created
**Problem:** Workflow runs but no PR appears  
**Solution:** Check if Anthropic is actually used
```bash
grep -r "Anthropic\|anthropic" . --include="*.ts" --include="*.py"
```
If nothing found, workflow correctly skips integration.

### Router Not Detected
**Problem:** Workflow doesn't find project type  
**Solution:** Ensure `package.json` or `requirements.txt` exists
```bash
ls package.json requirements.txt  # Must find at least one
```

---

## 💰 Calculate Your Savings

**For 50 sites:**
- Per site: $20-50/month
- Total: $1,000-2,500/month
- **Annual: $12,000-30,000**

**For 100 sites:**
- Per site: $20-50/month
- Total: $2,000-5,000/month
- **Annual: $24,000-60,000**

**As you add sites:**
- Each new site: +$20-50/month (automated)
- Total scales automatically
- Zero marginal effort

---

## 🎯 Next Steps

### Today:
1. Copy workflow to first project repo
2. Push to trigger it
3. Review and merge PR
4. Watch savings start

### This Week:
5. Add workflow to all 50 sites (use batch script)
6. All workflows run on next push
7. All 50 PRs created automatically
8. Merge all 50 → Full integration

### Going Forward:
9. Every new project auto-integrates
10. Savings scale infinitely
11. Zero manual work needed

---

## 📁 Files in This Repo

- `.github/workflows/auto-integrate-router.yml` — Use for most projects
- `.github/workflows/reusable-router-setup.yml` — Use for complex CI
- `skill_implementation.py` — Core automation logic
- `GITHUB_ACTIONS_AUTOMATION.md` — This guide

---

## 🔗 Resources

- [Free Token Router Repo](https://github.com/lanardisaac-max/free-token-router)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Ready to automate 50+ sites? Add the workflow and push.** 🚀

Everything else happens automatically.
