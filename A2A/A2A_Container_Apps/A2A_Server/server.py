from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import A2AAgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
import uvicorn
import os

def main():
    # creating the agent skill for MCP A2A Foundry integration
    skill = AgentSkill(
        id = "mcp_a2a_foundry_agent_skill",
        name = "This skill interacts with Microsoft Foundry via MCP Server",
        description = "This skill allows the agent to interact with Microsoft Foundry using the MCP Server connection to provide users with relevant learning resources and information about Microsoft technologies.",
        tags = ["mcp a2a foundry agent"],
        examples = ["Give me code to interact with Microsoft Foundry using the Python SDK.", "How to provision an azure storage account using the Azure CLI?"]
    )

    # creating the public agent card for MCP A2A Foundry integration
    public_agent_card = AgentCard(
        name = "A2A MCP Foundry Demo Agent",
        description = "Foundry Demo Agent to Show A2A Usage with Microsoft Foundry and MCP Server",
        url = os.environ.get("AGENT_CARD_URL"),
        version = "1.0.0",
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills = [skill]
    )
    
  
    # creating the request handler
    request_handler = DefaultRequestHandler(
        agent_executor = A2AAgentExecutor(),
        task_store = InMemoryTaskStore()
    )

    # creating the A2A Starlette application
    server = A2AStarletteApplication(
        agent_card = public_agent_card,
        http_handler = request_handler
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()