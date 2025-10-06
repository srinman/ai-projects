# MAF - Microsoft Agent Framework - Simple test


https://azure.microsoft.com/en-us/blog/introducing-microsoft-agent-framework/  


```bash
pip install agent-framework
``` 


Find values for the following env. 

Open ai.azure.com 
Create a new project or use an existing one.  
Note down Azure AI Foundry project endpoint.   
Deploy a new model or use an existing one. 
Note down name of the model deployment.   



```bash
export AZURE_AI_PROJECT_ENDPOINT="https://ai-training-project-resource.services.ai.azure.com/api/projects/ai-training-project"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"
```


```bash
python3 agent-ai.py
```


