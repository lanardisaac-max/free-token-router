#!/bin/bash
# Free Token Router - Complete Setup Script
# Run this to deploy to GitHub and Railway

set -e  # Exit on error

echo "================================"
echo "Free Token Router Setup"
echo "================================"
echo ""

# Configuration
REPO_NAME="free-token-router"
GITHUB_USERNAME=${GITHUB_USERNAME:-"lanardisaac-max"}
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "📋 Configuration:"
echo "  Repository: $REPO_NAME"
echo "  GitHub user: $GITHUB_USERNAME"
echo "  URL: $REPO_URL"
echo ""

# Step 1: Verify files exist
echo "✅ Step 1: Verifying files..."
required_files=("app.py" "requirements.txt" "railway.json" "README.md" "DEPLOYMENT_GUIDE.md" ".env.example")
for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "❌ Missing: $file"
    exit 1
  fi
done
echo "✅ All files present"
echo ""

# Step 2: Initialize Git
echo "✅ Step 2: Initializing Git repository..."
if [ ! -d ".git" ]; then
  git init
  echo "✅ Git initialized"
else
  echo "⚠️  Git already initialized"
fi
echo ""

# Step 3: Configure Git
echo "✅ Step 3: Configuring Git..."
git config user.email "lanard.isaac@gmail.com" 2>/dev/null || true
git config user.name "Lanard Isaac" 2>/dev/null || true
echo "✅ Git configured"
echo ""

# Step 4: Add and commit files
echo "✅ Step 4: Staging files..."
git add .
echo "✅ Files staged"
echo ""

echo "✅ Step 5: Creating initial commit..."
git commit -m "Initial commit: Free token router service

- FastAPI router aggregating Claude, OpenAI, Cohere APIs
- Intelligent provider selection with failover
- Load balancing across free tier providers
- 2.5M+ free tokens/month
- Ready for deployment to Railway" 2>/dev/null || echo "⚠️  No changes to commit"
echo ""

# Step 6: Add remote
echo "✅ Step 6: Adding GitHub remote..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
echo "✅ Remote added: $REPO_URL"
echo ""

# Step 7: Push to GitHub
echo "✅ Step 7: Pushing to GitHub..."
echo "  (You may be prompted for GitHub credentials)"
git push -u origin main 2>/dev/null || {
  echo ""
  echo "⚠️  Push failed. Possible reasons:"
  echo "  1. Repository doesn't exist on GitHub yet"
  echo "  2. Authentication failed"
  echo ""
  echo "  Manual steps:"
  echo "    1. Create repo: https://github.com/new"
  echo "       Name: $REPO_NAME"
  echo "       (Keep other settings default)"
  echo "    2. Then run: git push -u origin main"
  exit 1
}
echo "✅ Pushed to GitHub"
echo ""

# Step 8: Display next steps
echo "================================"
echo "✅ GitHub Setup Complete!"
echo "================================"
echo ""
echo "📍 Repository: $REPO_URL"
echo ""
echo "🚀 Next: Deploy to Railway"
echo ""
echo "   Option A (CLI):"
echo "     npm install -g @railway/cli"
echo "     railway login"
echo "     railway up"
echo ""
echo "   Option B (Dashboard):"
echo "     1. Go to https://railway.app"
echo "     2. Click 'Create Project'"
echo "     3. Select 'Deploy from GitHub'"
echo "     4. Select this repository"
echo "     5. Click 'Deploy'"
echo ""
echo "3️⃣  After deployment:"
echo "   1. Get your Railway URL"
echo "   2. Add environment variables:"
echo "      - ANTHROPIC_API_KEY=sk-ant-xxxxx"
echo "      - OPENAI_API_KEY=sk-xxxxx"
echo "      - COHERE_API_KEY=xxxxx"
echo "   3. Test: curl https://your-railway-url/health"
echo ""
echo "================================"
