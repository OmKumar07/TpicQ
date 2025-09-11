# TpicQ Azure Deployment Guide

## Prerequisites
1. Azure Account with active subscription
2. Azure CLI installed on your machine
3. Git repository (your code)

## Option 1: Azure App Service (Recommended)

### Step 1: Install Azure CLI
```bash
# Download and install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

### Step 2: Login to Azure
```bash
az login
```

### Step 3: Create Resource Group
```bash
az group create --name tpicq-rg --location "East US"
```

### Step 4: Create App Service Plan
```bash
az appservice plan create \
  --name tpicq-plan \
  --resource-group tpicq-rg \
  --sku B1 \
  --is-linux
```

### Step 5: Create Web App
```bash
az webapp create \
  --resource-group tpicq-rg \
  --plan tpicq-plan \
  --name your-tpicq-app \
  --runtime "PYTHON|3.11" \
  --deployment-local-git
```

### Step 6: Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group tpicq-rg \
  --name your-tpicq-app \
  --settings \
    GEMINI_API_KEY_1="your_first_api_key" \
    GEMINI_API_KEY_2="your_second_api_key" \
    GEMINI_API_KEY_3="your_third_api_key" \
    GEMINI_API_KEY_4="your_fourth_api_key" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    WEBSITES_PORT=8000
```

### Step 7: Configure Startup Command
```bash
az webapp config set \
  --resource-group tpicq-rg \
  --name your-tpicq-app \
  --startup-file "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"
```

### Step 8: Deploy Code
```bash
# Get deployment URL
az webapp deployment source config-local-git \
  --name your-tpicq-app \
  --resource-group tpicq-rg

# Add Azure remote
git remote add azure https://your-tpicq-app.scm.azurewebsites.net:443/your-tpicq-app.git

# Deploy
git push azure main
```

## Option 2: Azure Container Instances

### Step 1: Create Dockerfile
```dockerfile
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/build ./backend/static
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Build and Push to Azure Container Registry
```bash
az acr create --resource-group tpicq-rg --name tpicqregistry --sku Basic
az acr build --registry tpicqregistry --image tpicq:latest .
```

### Step 3: Deploy Container
```bash
az container create \
  --resource-group tpicq-rg \
  --name tpicq-container \
  --image tpicqregistry.azurecr.io/tpicq:latest \
  --dns-name-label tpicq-unique \
  --ports 8000 \
  --environment-variables \
    GEMINI_API_KEY_1=your_key_1 \
    GEMINI_API_KEY_2=your_key_2 \
    GEMINI_API_KEY_3=your_key_3 \
    GEMINI_API_KEY_4=your_key_4
```

## Option 3: Azure Static Web Apps + Functions

### Step 1: Create Static Web App
```bash
az staticwebapp create \
  --name tpicq-swa \
  --resource-group tpicq-rg \
  --source https://github.com/yourusername/TpicQ \
  --location "East US 2" \
  --branch main \
  --app-location "frontend" \
  --api-location "api" \
  --output-location "build"
```

## Environment Variables Setup

After deployment, your app will be available at:
- App Service: `https://your-tpicq-app.azurewebsites.net`
- Container: `http://tpicq-unique.eastus.azurecontainer.io:8000`
- Static Web App: `https://your-static-app.azurestaticapps.net`

## Post-Deployment Checklist

1. ✅ Verify all 4 API keys are configured
2. ✅ Test quiz generation functionality
3. ✅ Check API key rotation is working
4. ✅ Verify frontend is serving correctly
5. ✅ Test all API endpoints
6. ✅ Monitor application logs

## Monitoring and Scaling

### Enable Application Insights
```bash
az extension add --name application-insights
az monitor app-insights component create \
  --app tpicq-insights \
  --location "East US" \
  --resource-group tpicq-rg
```

### Scale Up (if needed)
```bash
az appservice plan update \
  --name tpicq-plan \
  --resource-group tpicq-rg \
  --sku P1V2
```

## Troubleshooting

### Common Issues:
1. **Build Failures**: Check `requirements.txt` and `package.json`
2. **API Key Issues**: Verify environment variables in Azure portal
3. **CORS Issues**: Update allowed origins in production
4. **Database Issues**: Consider Azure Database for PostgreSQL for production

### Logs:
```bash
az webapp log tail --name your-tpicq-app --resource-group tpicq-rg
```

## Cost Optimization

- Use B1 tier for development/testing
- Upgrade to P1V2+ for production
- Monitor usage with Azure Cost Management
- Set up billing alerts

## Security Best Practices

1. Enable HTTPS only
2. Configure custom domain with SSL
3. Set up API Management for rate limiting
4. Use Azure Key Vault for sensitive data
5. Enable Application Gateway for additional security

Replace `your-tpicq-app` with your desired app name and update API keys accordingly.
