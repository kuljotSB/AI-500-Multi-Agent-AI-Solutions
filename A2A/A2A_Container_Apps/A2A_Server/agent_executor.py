from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_text_artifact
from a2a_agent_class import A2AAgent
import os

class A2AAgentExecutor(AgentExecutor):
    def __init__(self):
        self.a2a_agent_object = A2AAgent(
            project_endpoint=os.environ.get("FOUNDRY_PROJECT_ENDPOINT"),
            model_deployment_name=os.environ.get("MODEL_DEPLOYMENT_NAME")
        )
        self.mcp_tool = None
        self.agent_created = False

    async def ensure_agent_ready(self):
        if not self.agent_created:
            self.mcp_tool = await self.a2a_agent_object.create_mcp_tool(
                mcp_tool_connection_name=os.environ.get("MCP_TOOL_CONNECTION_NAME"),
                mcp_server_url=os.environ.get("MCP_SERVER_URL")
            )
            await self.a2a_agent_object.create_agent(
                agent_name="MCP-Integrated-Agent",
                mcp_tool=self.mcp_tool
            )
            await self.a2a_agent_object.create_conversation()
            self.agent_created = True

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        if not self.agent_created:
         await self.ensure_agent_ready()
        query = context.get_user_input()
        if not context.message:
            raise Exception("No message found in the request context.")
        
        print(f"Received user query: {query}")
        print("Invoking agent...")
        async for event in self.a2a_agent_object.invoke_agent_stream(
            user_input=query
        ):
            message = TaskArtifactUpdateEvent(
                context_id=context.context_id,  # type: ignore
                task_id=context.task_id,  # type: ignore
                artifact=new_text_artifact(
                    name='current_result',
                    text=event['content'],
                ),
            )
            await event_queue.enqueue_event(message)
            if event['done']:
                break

        status = TaskStatusUpdateEvent(
            context_id=context.context_id,  # type: ignore
            task_id=context.task_id,  # type: ignore
            status=TaskStatus(state=TaskState.completed),
            final=True,
        )
        await event_queue.enqueue_event(status)

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')