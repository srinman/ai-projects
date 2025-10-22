


helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
    --namespace kagent \
    --create-namespace



../.env


helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
    --namespace kagent \
    --create-namespace


helm install kagent oci://ghcr.io/kagent-dev/kagent/helm/kagent \
    --namespace kagent \
    --set providers.default=azureOpenAI \
    --set providers.azureOpenAI.apiKey=$AZURE_OPENAI_API_KEY \
    --set providers.azureOpenAI.endpoint=$AZURE_OPENAI_ENDPOINT


helm uninstall kagent -n kagent
helm uninstall kagent-crds -n kagent
