# TpicQ Azure Deployment Script (PowerShell)
# Make sure you're logged in: az login

param(
    [string]$ResourceGroup = "tpicq-rg",
    [string]$AppName = "tpicq-quiz-app-$(Get-Random -Minimum 1000 -Maximum 9999)",
    [string]$Location = "East US",
    [string]$PlanName = "tpicq-plan"
)

Write-Host "🚀 Deploying TpicQ to Azure..." -ForegroundColor Green

# Create resource group
Write-Host "📦 Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location

# Create App Service plan
Write-Host "📋 Creating App Service plan..." -ForegroundColor Yellow
az appservice plan create `
  --name $PlanName `
  --resource-group $ResourceGroup `
  --sku B1 `
  --is-linux

# Create web app
Write-Host "🌐 Creating Web App..." -ForegroundColor Yellow
az webapp create `
  --resource-group $ResourceGroup `
  --plan $PlanName `
  --name $AppName `
  --runtime "PYTHON|3.11" `
  --deployment-local-git

# Configure startup command
Write-Host "⚙️ Configuring startup command..." -ForegroundColor Yellow
az webapp config set `
  --resource-group $ResourceGroup `
  --name $AppName `
  --startup-file "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

# Configure app settings
Write-Host "🔧 Setting environment variables..." -ForegroundColor Yellow
Write-Host "Please enter your Gemini API keys:" -ForegroundColor Cyan

$ApiKey1 = Read-Host "API Key 1"
$ApiKey2 = Read-Host "API Key 2"
$ApiKey3 = Read-Host "API Key 3"
$ApiKey4 = Read-Host "API Key 4"

az webapp config appsettings set `
  --resource-group $ResourceGroup `
  --name $AppName `
  --settings `
    GEMINI_API_KEY_1="$ApiKey1" `
    GEMINI_API_KEY_2="$ApiKey2" `
    GEMINI_API_KEY_3="$ApiKey3" `
    GEMINI_API_KEY_4="$ApiKey4" `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    WEBSITES_PORT=8000

# Enable local git deployment
Write-Host "🔗 Setting up git deployment..." -ForegroundColor Yellow
$DeployUrl = az webapp deployment source config-local-git `
  --name $AppName `
  --resource-group $ResourceGroup `
  --query url -o tsv

Write-Host "✅ Deployment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Deployment URL: $DeployUrl" -ForegroundColor Cyan
Write-Host "🌐 App URL: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "1. Add Azure remote: git remote add azure $DeployUrl" -ForegroundColor White
Write-Host "2. Deploy code: git push azure main" -ForegroundColor White
Write-Host "3. Monitor logs: az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor White
