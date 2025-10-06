import asyncio
import os
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async def main():
    # Get environment variables
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    
    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
    if not deployment_name:
        raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME environment variable is required")
    
    print(f"Using endpoint: {endpoint}")
    print(f"Using deployment: {deployment_name}")
    
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(
                async_credential=credential,
                endpoint=endpoint,
                deployment_name=deployment_name
            ),
            instructions="You are good at telling jokes."
        ) as agent,
    ):
        result = await agent.run("Tell me a joke about a pirate.")
        print(result.text)

if __name__ == "__main__":
    asyncio.run(main())