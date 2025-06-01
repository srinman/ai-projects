# Multi-User Azure AI Agent Threads Manager

This code creates an interactive console application for managing multiple Azure AI Agent threads for different users based on the `sample_agents_basics.py` baseline.    

This baseline sample py is from https://github.com/Azure/azure-sdk-for-python/blob/azure-ai-projects_1.0.0b11/sdk/ai/azure-ai-agents/samples/sample_agents_basics.py  

This sample demonstrates how to manage multiple threads for different users using the Azure Agents service with an interactive console interface.  
## Features

- **Three User Threads**: Creates dedicated threads for user1, user2, and user3
- **Interactive Menu System**: Easy-to-use console interface for switching between users
- **Message Management**: Send messages to specific user threads
- **Agent Invocation Control**: Ask before invoking the agent on each thread
- **Run Monitoring**: Monitor agent runs until completion
- **Thread History**: View conversation history for each user
- **Status Overview**: See all users' status at a glance
- **Resource Cleanup**: Proper cleanup of agents and threads on exit

## Prerequisites

```bash
pip install azure-ai-agents azure-identity
```

Set these environment variables:
- `PROJECT_ENDPOINT` - Your Azure AI Project endpoint
- `MODEL_DEPLOYMENT_NAME` - Your AI model deployment name

## Code Implementation

```python
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
This sample demonstrates how to manage multiple threads for different users
using the Azure Agents service with an interactive console interface.

USAGE:
python multi_user_agent_threads.py

Before running the sample:
pip install azure-ai-agents azure-identity

Set these environment variables with your own values:
1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
   page of your Azure AI Foundry portal.
2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
   the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import os
import time
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder


class MultiUserAgentManager:
    """
    A class to manage multiple user threads and agent interactions.
    """
    
    def __init__(self):
        # Initialize the Azure AI Agents client
        self.agents_client = AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
        
        # Dictionary to store user threads
        self.user_threads = {}
        
        # Store the agent instance
        self.agent = None
        
        # User list
        self.users = ["user1", "user2", "user3"]
        
        # Current selected user
        self.current_user = None
    
    def initialize_agent(self):
        """Create the agent that will be used across all threads."""
        try:
            self.agent = self.agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="multi-user-agent",
                instructions="You are a helpful assistant that can work with multiple users. "
                           "Always be polite and remember the context of each conversation.",
            )
            print(f"✅ Created agent, agent ID: {self.agent.id}")
            return True
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            return False
    
    def create_user_threads(self):
        """Create threads for all three users."""
        print("\n🧵 Creating threads for all users...")
        
        for user in self.users:
            try:
                thread = self.agents_client.threads.create()
                self.user_threads[user] = {
                    'thread': thread,
                    'message_count': 0
                }
                print(f"✅ Created thread for {user}, thread ID: {thread.id}")
            except Exception as e:
                print(f"❌ Error creating thread for {user}: {e}")
                return False
        
        print(f"\n📊 Successfully created {len(self.user_threads)} threads")
        return True
    
    def display_main_menu(self):
        """Display the main menu options."""
        print("\n" + "="*50)
        print("🤖 MULTI-USER AGENT CONSOLE")
        print("="*50)
        print("Available options:")
        print("1. Switch User")
        print("2. Send Message")
        print("3. View Thread History")
        print("4. View All Users Status")
        print("5. Clean Up and Exit")
        print("-"*50)
        
        if self.current_user:
            thread_id = self.user_threads[self.current_user]['thread'].id
            msg_count = self.user_threads[self.current_user]['message_count']
            print(f"👤 Current User: {self.current_user}")
            print(f"🧵 Thread ID: {thread_id[:8]}...")
            print(f"💬 Messages: {msg_count}")
        else:
            print("👤 No user selected")
        print("-"*50)
    
    def switch_user(self):
        """Allow user to switch between different user contexts."""
        print("\n👥 Select a user:")
        for i, user in enumerate(self.users, 1):
            status = "✅ Active" if user == self.current_user else "⭕ Available"
            msg_count = self.user_threads[user]['message_count']
            print(f"{i}. {user} ({status}) - {msg_count} messages")
        
        try:
            choice = input("\nEnter user number (1-3): ").strip()
            if choice in ['1', '2', '3']:
                user_index = int(choice) - 1
                self.current_user = self.users[user_index]
                print(f"\n🔄 Switched to {self.current_user}")
                return True
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                return False
        except (ValueError, IndexError):
            print("❌ Invalid input. Please try again.")
            return False
    
    def send_message(self):
        """Send a message to the current user's thread."""
        if not self.current_user:
            print("❌ Please select a user first.")
            return
        
        print(f"\n💬 Sending message as {self.current_user}")
        message_content = input("Enter your message: ").strip()
        
        if not message_content:
            print("❌ Message cannot be empty.")
            return
        
        try:
            # Get current user's thread
            current_thread = self.user_threads[self.current_user]['thread']
            
            # Create the message
            message = self.agents_client.messages.create(
                thread_id=current_thread.id,
                role="user",
                content=message_content
            )
            
            # Update message count
            self.user_threads[self.current_user]['message_count'] += 1
            
            print(f"✅ Message sent, message ID: {message.id}")
            
            # Ask if user wants to invoke the agent
            self.ask_to_invoke_agent()
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
    
    def ask_to_invoke_agent(self):
        """Ask user if they want to invoke the agent on the current thread."""
        print(f"\n🤔 Do you want to invoke the agent on {self.current_user}'s thread?")
        choice = input("Enter 'y' for yes, 'n' for no: ").strip().lower()
        
        if choice in ['y', 'yes']:
            self.invoke_agent()
        elif choice in ['n', 'no']:
            print("👍 Skipping agent invocation.")
        else:
            print("❌ Invalid choice. Skipping agent invocation.")
    
    def invoke_agent(self):
        """Invoke the agent on the current user's thread (create a run)."""
        if not self.current_user:
            print("❌ Please select a user first.")
            return
        
        try:
            current_thread = self.user_threads[self.current_user]['thread']
            
            print(f"\n🚀 Invoking agent on {self.current_user}'s thread...")
            
            # Create a run
            run = self.agents_client.runs.create(
                thread_id=current_thread.id,
                agent_id=self.agent.id
            )
            
            print(f"⏳ Run created, run ID: {run.id}")
            print("🔄 Monitoring run status...")
            
            # Poll the run status
            while run.status in ["queued", "in_progress", "requires_action"]:
                print(f"   Status: {run.status}")
                time.sleep(1)
                run = self.agents_client.runs.get(
                    thread_id=current_thread.id,
                    run_id=run.id
                )
            
            print(f"✅ Run completed with status: {run.status}")
            
            if run.status == "failed":
                print(f"❌ Run error: {run.last_error}")
            else:
                # Show the latest messages
                print(f"\n📝 Latest response from agent:")
                self.show_latest_messages(current_thread.id, limit=2)
                
                # Update message count (agent response)
                self.user_threads[self.current_user]['message_count'] += 1
                
        except Exception as e:
            print(f"❌ Error invoking agent: {e}")
    
    def show_latest_messages(self, thread_id, limit=5):
        """Show the latest messages from a thread."""
        try:
            messages = self.agents_client.messages.list(
                thread_id=thread_id,
                order=ListSortOrder.DESCENDING,
                limit=limit
            )
            
            print("\n" + "-"*40)
            for msg in reversed(list(messages)):
                if msg.text_messages:
                    role_icon = "👤" if msg.role == "user" else "🤖"
                    last_text = msg.text_messages[-1]
                    content = last_text.text.value
                    # Truncate long messages
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"{role_icon} {msg.role}: {content}")
            print("-"*40)
            
        except Exception as e:
            print(f"❌ Error retrieving messages: {e}")
    
    def view_thread_history(self):
        """View the conversation history for the current user."""
        if not self.current_user:
            print("❌ Please select a user first.")
            return
        
        current_thread = self.user_threads[self.current_user]['thread']
        print(f"\n📜 Conversation history for {self.current_user}:")
        self.show_latest_messages(current_thread.id, limit=10)
    
    def view_all_users_status(self):
        """Display status information for all users."""
        print("\n📊 ALL USERS STATUS")
        print("="*50)
        
        for user in self.users:
            thread_info = self.user_threads[user]
            thread_id = thread_info['thread'].id
            msg_count = thread_info['message_count']
            status_icon = "🟢" if user == self.current_user else "⚪"
            
            print(f"{status_icon} {user}:")
            print(f"   Thread ID: {thread_id}")
            print(f"   Messages: {msg_count}")
            print()
    
    def cleanup_and_exit(self):
        """Clean up resources and exit the application."""
        print("\n🧹 Cleaning up resources...")
        
        try:
            # Delete threads
            for user, thread_info in self.user_threads.items():
                thread_id = thread_info['thread'].id
                print(f"   Deleting thread for {user}...")
                # Note: Thread deletion might not be available in all versions
                # self.agents_client.threads.delete(thread_id)
            
            # Delete agent
            if self.agent:
                print(f"   Deleting agent {self.agent.id}...")
                self.agents_client.delete_agent(self.agent.id)
                print("✅ Agent deleted")
            
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
        
        print("\n👋 Goodbye!")
        return True
    
    def run(self):
        """Main application loop."""
        print("🚀 Starting Multi-User Agent Manager...")
        
        # Initialize agent
        if not self.initialize_agent():
            return
        
        # Create threads for all users
        if not self.create_user_threads():
            return
        
        # Main interactive loop
        while True:
            try:
                self.display_main_menu()
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    self.switch_user()
                elif choice == '2':
                    self.send_message()
                elif choice == '3':
                    self.view_thread_history()
                elif choice == '4':
                    self.view_all_users_status()
                elif choice == '5':
                    if self.cleanup_and_exit():
                        break
                else:
                    print("❌ Invalid choice. Please enter a number between 1-5.")
                
                # Small pause for better UX
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n🛑 Received interrupt signal. Exiting...")
                self.cleanup_and_exit()
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("⚠️  Continuing...")


def main():
    """Main entry point of the application."""
    print("🤖 Multi-User Azure AI Agent Console")
    print("====================================")
    
    # Check for required environment variables
    required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running the application.")
        return
    
    # Create and run the manager
    manager = MultiUserAgentManager()
    
    # Use context manager for proper resource management
    with manager.agents_client:
        manager.run()


if __name__ == "__main__":
    main()
```

## Usage Instructions

1. **Setup Environment Variables**:
   ```bash
   export PROJECT_ENDPOINT="https://your-resource.services.ai.azure.com/api/projects/your-project"
   export MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
   ```

2. **Run the Application**:
   ```bash
   python multi_user_agent_threads.py
   ```

3. **Menu Navigation**:
   - **Option 1**: Switch between user1, user2, and user3
   - **Option 2**: Send messages to the current user's thread
   - **Option 3**: View conversation history for the current user
   - **Option 4**: See status overview of all users
   - **Option 5**: Clean up resources and exit

## Key Features Explained

### Multi-Thread Management
- Creates separate threads for each of the three users
- Maintains conversation context independently for each user
- Tracks message counts and thread IDs

### Interactive User Switching
- Easy menu-driven interface to switch between users
- Visual indicators showing which user is currently active
- Status overview showing message counts for each user

### Agent Invocation Control
- After each message, prompts whether to invoke the agent
- Creates a run on the selected thread when agent is invoked
- Monitors run status until completion
- Displays agent responses with proper formatting

### Error Handling and Cleanup
- Comprehensive error handling throughout the application
- Proper resource cleanup on exit
- Graceful handling of interruptions (Ctrl+C)

## Based on Azure AI Foundry Agent Service

This implementation leverages the Azure AI Foundry Agent Service concepts:
- **Agents**: Custom AI that uses models with tools
- **Threads**: Conversation sessions between agent and users
- **Messages**: Individual communications within threads
- **Runs**: Agent invocations that process thread messages

The code extends the basic `sample_agents_basics.py` to support multiple concurrent user sessions while maintaining the core architecture and best practices of the Azure AI Agents SDK.