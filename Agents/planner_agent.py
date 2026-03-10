from pydantic import BaseModel, Field
from agents import Agent

HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"""You are a helpful research assistant. 
Given a user query, generate a set of web search terms that would best help answer it. 
Output exactly {HOW_MANY_SEARCHES} search terms."""


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")
    
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)