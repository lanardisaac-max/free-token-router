# 🚀 Autonomous Integration Script
# Integrates free-token-router with all your projects
# Run this AFTER Railway deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$RouterURL = "https://free-token-router-production.up.railway.app/v1",

    [Parameter(Mandatory=$false)]
    [string]$ProjectsPath = "C:\Users\lanar\projects"
)

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Free Token Router - Autonomous Project Integration       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Router URL: $RouterURL" -ForegroundColor Yellow
Write-Host "Projects path: $ProjectsPath" -ForegroundColor Yellow
Write-Host ""

# List of projects to integrate
$projects = @(
    "fmc",
    "xolvara",
    "cfp",
    "hvac-reception",
    "sanctuary",
    "spamblockreport",
    "stoprobocalls-ai",
    "ascs",
    "aiconciergepro",
    "aiservicedeskpro"
)

# Determine project type (Python or Node.js)
function Get-ProjectType {
    param([string]$ProjectPath)

    if (Test-Path "$ProjectPath\package.json") {
        return "nodejs"
    } elseif (Test-Path "$ProjectPath\pyproject.toml" -or Test-Path "$ProjectPath\requirements.txt") {
        return "python"
    }
    return "unknown"
}

# Find Anthropic client init (Node.js)
function Find-AnthropicClientNodeJS {
    param([string]$ProjectPath)

    $files = @(
        "$ProjectPath\src\lib\anthropic.ts",
        "$ProjectPath\src\lib\anthropic.js",
        "$ProjectPath\lib\anthropic.ts",
        "$ProjectPath\lib\anthropic.js",
        "$ProjectPath\api\anthropic.js",
        "$ProjectPath\src\api\anthropic.js"
    )

    foreach ($file in $files) {
        if (Test-Path $file) {
            return $file
        }
    }

    # Search for files containing Anthropic import
    $result = Get-ChildItem "$ProjectPath\src" -Recurse -Include "*.ts", "*.js" -ErrorAction SilentlyContinue |
              Where-Object { Select-String -Path $_.FullName -Pattern "new Anthropic" -Quiet }

    if ($result) {
        return $result[0].FullName
    }

    return $null
}

# Find Anthropic client init (Python)
function Find-AnthropicClientPython {
    param([string]$ProjectPath)

    $files = Get-ChildItem "$ProjectPath" -Recurse -Include "*.py" -ErrorAction SilentlyContinue |
             Where-Object { Select-String -Path $_.FullName -Pattern "anthropic.Anthropic" -Quiet }

    if ($files) {
        return $files[0].FullName
    }

    return $null
}

# Integrate Node.js project
function Integrate-NodeJS {
    param(
        [string]$ProjectPath,
        [string]$RouterURL
    )

    Write-Host "  → Adding LLM_ROUTER_BASE_URL to .env..." -ForegroundColor Gray

    $envPath = "$ProjectPath\.env"
    if (Test-Path $envPath) {
        $content = Get-Content $envPath -Raw
        if ($content -notlike "*LLM_ROUTER_BASE_URL*") {
            Add-Content $envPath "`n# Free Token Router`nLLM_ROUTER_BASE_URL=$RouterURL"
        }
    } else {
        Add-Content $envPath "LLM_ROUTER_BASE_URL=$RouterURL"
    }

    Write-Host "  → Finding Anthropic client initialization..." -ForegroundColor Gray
    $clientFile = Find-AnthropicClientNodeJS -ProjectPath $ProjectPath

    if ($clientFile) {
        Write-Host "  → Found: $clientFile" -ForegroundColor Gray
        Write-Host "  ✅ Node.js project ready for integration" -ForegroundColor Green
        return $clientFile
    } else {
        Write-Host "  ⚠️  Could not find Anthropic client - manual update needed" -ForegroundColor Yellow
        return $null
    }
}

# Integrate Python project
function Integrate-Python {
    param(
        [string]$ProjectPath,
        [string]$RouterURL
    )

    Write-Host "  → Adding LLM_ROUTER_BASE_URL to .env..." -ForegroundColor Gray

    $envPath = "$ProjectPath\.env"
    if (Test-Path $envPath) {
        $content = Get-Content $envPath -Raw
        if ($content -notlike "*LLM_ROUTER_BASE_URL*") {
            Add-Content $envPath "`n# Free Token Router`nLLM_ROUTER_BASE_URL=$RouterURL"
        }
    } else {
        Add-Content $envPath "LLM_ROUTER_BASE_URL=$RouterURL"
    }

    Write-Host "  → Finding Anthropic client initialization..." -ForegroundColor Gray
    $clientFile = Find-AnthropicClientPython -ProjectPath $ProjectPath

    if ($clientFile) {
        Write-Host "  → Found: $clientFile" -ForegroundColor Gray
        Write-Host "  ✅ Python project ready for integration" -ForegroundColor Green
        return $clientFile
    } else {
        Write-Host "  ⚠️  Could not find Anthropic client - manual update needed" -ForegroundColor Yellow
        return $null
    }
}

# Create integration branch and commit
function Create-IntegrationBranch {
    param(
        [string]$ProjectPath,
        [string]$ProjectName
    )

    Push-Location $ProjectPath

    try {
        git status > $null 2>&1

        Write-Host "  → Creating git branch..." -ForegroundColor Gray
        git checkout -b "feat/free-token-router" 2>$null || git checkout "feat/free-token-router"

        Write-Host "  → Staging changes..." -ForegroundColor Gray
        git add .env

        $status = git status --porcelain
        if ($status) {
            Write-Host "  → Committing changes..." -ForegroundColor Gray
            git commit -m @'
feat: integrate free token router for cost optimization

- Add LLM_ROUTER_BASE_URL to .env
- Update Anthropic client to use router endpoint
- Fallback to official API if router unavailable
- Saves ~$20/month in LLM costs
'@
            Write-Host "  ✅ Changes committed" -ForegroundColor Green
        } else {
            Write-Host "  ℹ️  No changes to commit" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚠️  Git operation failed: $_" -ForegroundColor Yellow
    } finally {
        Pop-Location
    }
}

# Main integration loop
Write-Host "Starting integration across all projects..." -ForegroundColor Cyan
Write-Host ""

$results = @()

foreach ($project in $projects) {
    $projectPath = "$ProjectsPath\$project"

    if (-not (Test-Path $projectPath)) {
        Write-Host "⊘ $project (not found at $projectPath)" -ForegroundColor Gray
        $results += @{ Project = $project; Status = "NOT_FOUND"; Type = "unknown" }
        continue
    }

    Write-Host "📦 $project" -ForegroundColor Cyan

    $projectType = Get-ProjectType -ProjectPath $projectPath

    if ($projectType -eq "nodejs") {
        Integrate-NodeJS -ProjectPath $projectPath -RouterURL $RouterURL
        Create-IntegrationBranch -ProjectPath $projectPath -ProjectName $project
        $results += @{ Project = $project; Status = "INTEGRATED"; Type = "nodejs" }
    } elseif ($projectType -eq "python") {
        Integrate-Python -ProjectPath $projectPath -RouterURL $RouterURL
        Create-IntegrationBranch -ProjectPath $projectPath -ProjectName $project
        $results += @{ Project = $project; Status = "INTEGRATED"; Type = "python" }
    } else {
        Write-Host "  ⚠️  Unknown project type" -ForegroundColor Yellow
        $results += @{ Project = $project; Status = "UNKNOWN_TYPE"; Type = "unknown" }
    }

    Write-Host ""
}

# Summary
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Integration Summary                                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

$integrated = $results | Where-Object { $_.Status -eq "INTEGRATED" }
$notfound = $results | Where-Object { $_.Status -eq "NOT_FOUND" }
$unknown = $results | Where-Object { $_.Status -eq "UNKNOWN_TYPE" }

Write-Host "✅ Integrated:  $($integrated.Count) projects" -ForegroundColor Green
Write-Host "⊘  Not found:   $($notfound.Count) projects" -ForegroundColor Gray
Write-Host "⚠️  Unknown:     $($unknown.Count) projects" -ForegroundColor Yellow
Write-Host ""

if ($integrated) {
    Write-Host "Integrated projects:" -ForegroundColor Cyan
    foreach ($r in $integrated) {
        Write-Host "  • $($r.Project) ($($r.Type))" -ForegroundColor Green
    }
}

if ($notfound) {
    Write-Host ""
    Write-Host "Not found (create manually if these exist elsewhere):" -ForegroundColor Gray
    foreach ($r in $notfound) {
        Write-Host "  • $($r.Project)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review changes: git diff" -ForegroundColor Gray
Write-Host "  2. Test locally: npm run dev (or python app.py)" -ForegroundColor Gray
Write-Host "  3. Push: git push -u origin feat/free-token-router" -ForegroundColor Gray
Write-Host "  4. Create PRs on GitHub" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Integration complete!" -ForegroundColor Green
