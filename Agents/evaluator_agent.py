from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from agents import Agent, ModelSettings, OpenAIChatCompletionsModel
import os

class EvaluationModel(BaseModel):
    valid: bool = Field(description="Whether the evaluated output is valid.")
    reason: str = Field(description="Brief explanation supporting the validity judgment.")

INSTRUCTIONS = (
    "You are an evaluation assistant. Your task is to determine whether the generated report "
    "correctly answers the research query.\n"
    "Evaluate the output based on:\n"
    "- relevance to the query\n"
    "- factual accuracy\n"
    "- clarity and organization\n"
    "- completeness of the report\n"
    "- whether the required fields are present\n\n"
    "If the report is valid, mark valid=True and return the evaluation result. Do NOT hand off.\n"
    "If the report is invalid, mark valid=False and hand off back to WriterAgent with a clear reason "
    "explaining exactly what needs to be fixed."
)
#gemini_client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=os.environ.get("GOOGLE_API_KEY"))
#gemini_model = OpenAIChatCompletionsModel(model="gemini-3-flash-preview", openai_client=gemini_client)

evaluator_agent = Agent(
    name="EvaluatorAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o",
    output_type=EvaluationModel,
    handoffs=[],
    handoff_description="Evaluates the generated report for relevance, accuracy, clarity, and completeness.",
    model_settings=ModelSettings(parallel_tool_calls=False)
    )