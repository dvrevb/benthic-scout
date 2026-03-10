from agents import Agent, WebSearchTool, ModelSettings

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, perform a web search and produce a concise summary "
    "of the results. The summary should be 2–3 paragraphs and under 300 words. Focus on capturing the main points "
    "clearly and succinctly—complete sentences or perfect grammar are not required. This summary will be used by someone "
    "synthesizing a report, so capturing the essence and omitting any fluff is vital. Include only the summary; do not "
    "add commentary or explanations."
)

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)