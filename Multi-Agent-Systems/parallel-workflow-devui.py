"""Vacation Planning Workflow Sample for DevUI.

This sample demonstrates a multi-agent workflow for vacation planning using the Microsoft Agent Framework.
Agents include: Location Picker, Destination Recommender, Weather, Cuisine Suggestion, and Itinerary Planner.
"""

# pip install agent-framework-devui==1.0.0b260918

import os
import asyncio
import logging
from dotenv import load_dotenv
from agent_framework import Agent
from azure.ai.projects import AIProjectClient
from agent_framework.foundry import FoundryAgent, FoundryChatClient, to_prompt_agent
from azure.identity import AzureCliCredential
from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler
from agent_framework import WorkflowBuilder, WorkflowViz
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from agent_framework.devui import serve

# Load environment variables
load_dotenv()
foundry_project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

print("Project Endpoint: ", foundry_project_endpoint)
print("Model: ", model_deployment_name)


# Async agent creation utility
async def create_agent(agent_name: str, agent_instructions: str) -> ChatAgent:
    credential = AzureCliCredential()

    client = FoundryChatClient(
        project_endpoint = foundry_project_endpoint,
        model = model_deployment_name,
        credential = credential
    )
    

    try:
        agent = Agent(
            client=client,

            name=agent_name,

            instructions=agent_instructions,

            tools=[
                FoundryChatClient.get_web_search_tool()
            ]
        )
        print(f"{agent_name} Agent created successfully!")
        return agent
    finally:
        await credential.close()


# Executor definitions
class LocationSelectorExecutor(Executor):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(self, user_query: str, ctx: WorkflowContext[str]) -> None:
        response = await self.agent.run(user_query)
        await ctx.send_message(str(response))

class DestinationRecommenderExecutor(Executor):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(self, location: str, ctx: WorkflowContext[str]) -> None:
        response = await self.agent.run(location)
        await ctx.send_message(str(response))

class WeatherExecutor(Executor):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(self, location: str, ctx: WorkflowContext[str]) -> None:
        response = await self.agent.run(location)
        await ctx.send_message(str(response))

class CuisineSuggestionExecutor(Executor):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(self, location: str, ctx: WorkflowContext[str]) -> None:
        response = await self.agent.run(location)
        await ctx.send_message(str(response))

class ItineraryPlannerExecutor(Executor):
    def __init__(self, agent, **kwargs):
        super().__init__(**kwargs)
        self.agent = agent

    @handler
    async def handle(self, results: list[str], ctx: WorkflowContext[str]) -> None:
        response = await self.agent.run(results)
        await ctx.yield_output(str(response))


async def build_workflow():
    # Create agents
    location_picker_agent = await create_agent(
        agent_name="Location-Picker-Agent",
        agent_instructions="You are a helpful assistant that helps users pick a location for their vacation."
    )
    destination_recommender_agent = await create_agent(
        agent_name="Destination-Recommender-Agent",
        agent_instructions="You are a travel expert that provides personalized vacation recommendations based on user preferences and locations."
    )
    weather_agent = await create_agent(
        agent_name="Weather-Agent",
        agent_instructions="You are a weather expert that provides accurate and up-to-date weather information for various locations selected"
    )
    cuisine_suggestion_agent = await create_agent(
        agent_name="Cuisine-Suggestion-Agent",
        agent_instructions="You are a culinary expert that suggests popular local cuisines and dining options based on the selected vacation destinations."
    )
    itinerary_planner_agent = await create_agent(
        agent_name="Itinerary-Planner-Agent",
        agent_instructions="You are an itinerary planning expert that creates detailed travel itineraries based on user preferences, selected destinations, weather conditions, and local cuisine options."
    )

    # Instantiate Executors
    location_selector_executor = LocationSelectorExecutor(location_picker_agent, id="LocationSelector")
    destination_recommender_executor = DestinationRecommenderExecutor(destination_recommender_agent, id="DestinationRecommender")
    weather_executor = WeatherExecutor(weather_agent, id="Weather")
    cuisine_suggestion_executor = CuisineSuggestionExecutor(cuisine_suggestion_agent, id="CuisineSuggestion")
    itinerary_planner_executor = ItineraryPlannerExecutor(itinerary_planner_agent, id="ItineraryPlanner")

    # Attach agents to executor state for handler access
    for executor in [
        location_selector_executor,
        destination_recommender_executor,
        weather_executor,
        cuisine_suggestion_executor,
        itinerary_planner_executor,
    ]:
        executor.state = {
            "location_picker_agent": location_picker_agent,
            "destination_recommender_agent": destination_recommender_agent,
            "weather_agent": weather_agent,
            "cuisine_suggestion_agent": cuisine_suggestion_agent,
            "itinerary_planner_agent": itinerary_planner_agent,
        }

    # Build the workflow
    workflow = (
        WorkflowBuilder(
            start_executor=location_selector_executor,
            name="Vacation Planner Workflow",
            description="Multi-agent workflow for vacation planning with recommendations and itinerary."
        )
        .add_fan_out_edges(location_selector_executor, [
            destination_recommender_executor,
            weather_executor,
            cuisine_suggestion_executor
        ])
        .add_fan_in_edges([
            destination_recommender_executor,
            weather_executor,
            cuisine_suggestion_executor
        ], itinerary_planner_executor)
        .build()
    )

    # Optionally, visualize the workflow (prints Mermaid diagram to console)
    viz = WorkflowViz(workflow)
    mermaid_content = viz.to_mermaid()
    print("Mermaid Diagram:\n", mermaid_content)

    return workflow


def main():
    """Launch the vacation planning workflow in DevUI."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Starting Vacation Planning Workflow")
    logger.info("Available at: http://localhost:8090")
    logger.info("Entity ID: workflow_vacation_planner")

    # Run async workflow builder and launch DevUI
    workflow = asyncio.run(build_workflow())
    serve(entities=[workflow], port=8090, auto_open=True)

if __name__ == "__main__":
    main()