# Azure AD Token Quick Reference

## Get Azure AD Token for Azure OpenAI (most common case)

### Quick Command:
```bash
az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken --output tsv
```

### For your Kagent ModelConfig:
```bash
# Get the token and save to variable
AZURE_AD_TOKEN=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken --output tsv)

# Display the token
echo $AZURE_AD_TOKEN

# Save to .env file
echo "AZURE_AD_TOKEN=$AZURE_AD_TOKEN" >> .env
```

## Different Resource Types:

1. **Azure OpenAI / Cognitive Services** (for your use case):
   ```bash
   az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken --output tsv
   ```

2. **Azure Resource Management**:
   ```bash
   az account get-access-token --resource https://management.azure.com/ --query accessToken --output tsv
   ```

3. **Microsoft Graph**:
   ```bash
   az account get-access-token --resource https://graph.microsoft.com --query accessToken --output tsv
   ```

## Prerequisites:
- Azure CLI installed (`az --version`)
- Logged in to Azure (`az login`)
- Proper permissions to the Azure OpenAI resource

## Update your Kagent ModelConfig:

Replace `<azure_ad_token_value>` in your YAML with the actual token:

```yaml
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: azuredefault-model-config
  namespace: kagent
spec:
  apiKeySecret: kagent-azureopenai
  apiKeySecretKey: AZURE_OPENAI_API_KEY
  model: gpt-4o-mini
  provider: AzureOpenAI
  azureOpenAI:
    azureEndpoint: "https://{yourendpointname}.openai.azure.com/"
    apiVersion: "2025-03-01-preview"
    azureDeployment: "gpt-4o-mini"
    azureAdToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6..." # Your actual token
```

## Helper Scripts:
- `./get-azure-token.sh` - Interactive bash script
- `python azure_token_helper.py` - Python script with more features

## Important Notes:
- Tokens expire after ~1 hour
- Don't commit tokens to git (they're in .env which is gitignored)
- For production, use managed identity or service principal instead of user tokens