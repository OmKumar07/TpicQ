#!/bin/bash

# TpicQ Azure Deployment Script
# Make sure you're logged in: az login

set -e

# Configuration
RESOURCE_GROUP="tpicq-rg"
APP_NAME="tpicq-quiz-app"
LOCATION="East US"
PLAN_NAME="tpicq-plan"

echo "🚀 Deploying TpicQ to Azure..."

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create App Service plan
echo "📋 Creating App Service plan..."
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create web app
echo "🌐 Creating Web App..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --name $APP_NAME \
  --runtime "PYTHON|3.11" \
  --deployment-local-git

# Configure startup command
echo "⚙️ Configuring startup command..."
az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --startup-file "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

# Configure app settings
echo "🔧 Setting environment variables..."
echo "Please enter your Gemini API keys:"
read -p "API Key 1: " API_KEY_1
read -p "API Key 2: " API_KEY_2
read -p "API Key 3: " API_KEY_3
read -p "API Key 4: " API_KEY_4

az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    GEMINI_API_KEY_1="$API_KEY_1" \
    GEMINI_API_KEY_2="$API_KEY_2" \
    GEMINI_API_KEY_3="$API_KEY_3" \
    GEMINI_API_KEY_4="$API_KEY_4" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    WEBSITES_PORT=8000

# Enable local git deployment
echo "🔗 Setting up git deployment..."
DEPLOY_URL=$(az webapp deployment source config-local-git \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query url -o tsv)

echo "✅ Deployment setup complete!"
echo ""
echo "🔗 Deployment URL: $DEPLOY_URL"
echo "🌐 App URL: https://$APP_NAME.azurewebsites.net"
echo ""
echo "📝 Next steps:"
echo "1. Add Azure remote: git remote add azure $DEPLOY_URL"
echo "2. Deploy code: git push azure main"
echo "3. Monitor logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
