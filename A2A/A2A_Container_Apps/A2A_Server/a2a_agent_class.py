import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import MCPTool, Tool
from azure.ai.projects.models import PromptAgentDefinition

class A2AAgent:
    def __init__(self,
                 project_endpoint: str,
                 model_deployment_name: str,
                 ):
        self.project_endpoint = project_endpoint
        self.model_deployment_name = model_deployment_name
        self.project_client = AIProjectClient(
            endpoint = self.project_endpoint,
            credential=DefaultAzureCredential()
        )
        self.openai_client = self.project_client.get_openai_client()
        self.mcp_tool = None
        self.agent = None
        self.conversation = None
    
    async def create_mcp_tool(self,
                              mcp_tool_connection_name: str,
                              mcp_server_url: str) -> MCPTool:
        mcp_tool_connection_id = ""
        # fetching the project connection id for the MCP Tool
        async for connection in self.project_client.connections.list():
            if connection.name == mcp_tool_connection_name:
                mcp_tool_connection_id = connection.id
                break
        if mcp_tool_connection_id == "":
            raise Exception(f"Connection with name {mcp_tool_connection_name} not found.")
        
        self.mcp_tool = MCPTool(
            server_label = mcp_tool_connection_name,
            server_url = mcp_server_url,
            project_connection_id = mcp_tool_connection_id,
            require_approval="never" 
        )
        
        print(f"MCP Tool created with connection id: {mcp_tool_connection_id}")
        return self.mcp_tool

    
    async def create_agent(self,
                           agent_name: str,
                           mcp_tool: MCPTool):
        
        print("Creating agent...")
        self.agent = await self.project_client.agents.create_version(
            agent_name = agent_name,
            definition = PromptAgentDefinition(
                model = self.model_deployment_name,
                instructions = "You are a helpful AI Assistant with tools integration.",
                tools = [mcp_tool]
            )
        )
    
    async def create_conversation(self):
        print("Creating conversation...")
        self.conversation = await self.openai_client.conversations.create()
    
    async def invoke_agent_stream(self,
                                  user_input: str
                                  ):
        try:
            response_stream_events = await self.openai_client.responses.create(
                conversation=self.conversation.id,
                extra_body = {
                    "agent": {
                        "name": self.agent.name,
                        "type": "agent_reference"
                    }
                },
                input = user_input,
                stream = True
            )
            
            async for event in response_stream_events:
                if event.type == "response.output_text.delta":
                        yield {'content': event.delta, 'done': False}
            yield {'content': '', 'done': True}

        except Exception as e:
            yield {
                'content': 'Sorry, an error occurred while processing your request.',
                'done': True,
            }
        
        