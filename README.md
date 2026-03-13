## benthic-scout

**benthic-scout** is an end‑to‑end “deep research” assistant. Given a natural‑language query, it:

- **Plans** targeted web searches
- **Runs** those searches and summarizes the results
- **Synthesizes** a long‑form, markdown research report (5–10 pages)
- **Evaluates & iterates** on the report quality
- **Emails** a nicely formatted HTML version of the report to a configured recipient

The whole flow can be driven through a minimal **Gradio** web UI.

---

## Features

- **Agentic research pipeline** built on `openai-agents`:
  - `PlannerAgent`: proposes web search queries for the topic
  - `Search agent`: executes web searches and summarizes results
  - `WriterAgent` + `EvaluatorAgent`: draft, critique, and refine a comprehensive report
  - `Email agent`: turns the report into HTML and sends it via SendGrid
- **Streaming UX** in the UI, showing status updates as the research progresses
- **Configurable models** (currently using `gpt-4o-mini` for most agents, `gpt-4o` for evaluation)
- **Environment‑based configuration** via `.env`

---

## Architecture Overview

### High‑level flow

The orchestration is handled by `ResearchManager` in `research_manager.py`:

1. **Plan searches**  
   - Uses `PlannerAgent` (`Agents/planner_agent.py`) to turn the user query into one or more `WebSearchItem`s grouped in a `WebSearchPlan`.
2. **Perform searches**  
   - Uses `Search agent` (`Agents/search_agent.py`) which is configured with `WebSearchTool` to hit the web and produce concise summaries.
3. **Write report**  
   - Uses `WriterAgent` (`Agents/writer_agent.py`) to:
     - Build an outline
     - Write a detailed markdown report
     - Optionally iterate based on feedback from `EvaluatorAgent`.
4. **Evaluate report**  
   - `EvaluatorAgent` (`Agents/evaluator_agent.py`) checks relevance, accuracy, clarity, and completeness using `EvaluationModel`.
   - If invalid, it hands back to `WriterAgent` with guidance to rewrite.
5. **Send email**  
   - `Email agent` (`Agents/email_agent.py`) converts the markdown into HTML and calls a `send_email` function‑tool backed by **SendGrid** to deliver the report.

### UI entrypoint

- `benthic_scout.py` defines a simple **Gradio Blocks** app:
  - A textbox for “What topic would you like to research?”
  - A **Run** button (and Enter key submit)
  - A markdown area that first shows progress messages, then the final report
- The app calls `ResearchManager().run(query)` as an async generator and streams partial updates to the UI.

---

## Requirements

- **Python**: `>= 3.12`
- See `pyproject.toml` for full dependencies; the main runtime libs are:
  - `gradio`
  - `openai-agents`
  - `pydantic`
  - `python-dotenv`
  - `sendgrid`

You’ll also need:

- An **OpenAI‑compatible** API key (for `openai-agents` to talk to `gpt-4o` / `gpt-4o-mini` or any configured model)
- A **SendGrid** account and API key (if you want the email step to run)

---

## Installation

From the project root:

```bash
uv sync
```

---

## Configuration

The app expects configuration via environment variables. A typical setup is to create a `.env` file in the project root (loaded in `benthic_scout.py` via `python-dotenv`).

### OpenAI / model configuration

`openai-agents` itself reads model and API configuration; depending on how you’ve set that up in your environment, you typically need:

- **`OPENAI_API_KEY`** (or equivalent for your provider)
- Optional base URL / organization variables if you’re pointing at a non‑default endpoint.

The individual agents are configured with:

- `PlannerAgent`, `Search agent`, `WriterAgent`, `Email agent`: `model="gpt-4o-mini"`
- `EvaluatorAgent`: `model="gpt-4o"`

You can change the `model` strings in the respective agent files if you want to target different models.

### SendGrid email settings

In `.env` (or your environment), define:

- `SENDGRID_API_KEY` – your SendGrid API key  
- `SENDGRID_FROM_EMAIL` – a verified sender address in SendGrid  
- `SENDGRID_TO_EMAIL` – the recipient address for the research report

Without these, the email step will fail; the rest of the pipeline (planning, searching, writing) will still work up until the email handoff.

---

## Running the app

From the project root:

```bash
uv run benthic_scout.py
```

This will:

- Start a Gradio Blocks interface (by default, on `http://127.0.0.1:7860`)
- Auto‑open your browser with the UI (`ui.launch(inbrowser=True)` in `benthic_scout.py`)

### Using the UI

1. Type your research topic in the textbox (e.g., “Long‑term impacts of deep‑sea mining on benthic ecosystems”).
2. Click **Run** or press **Enter**.
3. Watch status messages appear:
   - “Searches planned, starting to search…”
   - “Searches complete, writing report…”
   - “Report written, sending email…”
   - “Email sent, research complete”
4. When finished, the final **markdown report** will be displayed in the UI.
5. If email is configured, you’ll also receive an HTML version in your inbox.

---

## CLI / programmatic usage

You can also drive the research pipeline programmatically without Gradio:

```python
import asyncio
from research_manager import ResearchManager

async def main():
    async for chunk in ResearchManager().run("Your research question here"):
        print(chunk)  # intermediate messages and finally the markdown report

asyncio.run(main())
```

This is useful if you want to integrate the pipeline into another application or a scheduled job.

---

## Agents in detail

- **`PlannerAgent` (`Agents/planner_agent.py`)**
  - Input: raw user query
  - Output: `WebSearchPlan` → a list of `WebSearchItem`s (`reason`, `query`)
  - Model: `gpt-4o-mini`

- **`Search agent` (`Agents/search_agent.py`)**
  - Tooling: `WebSearchTool(search_context_size="low")`
  - Behavior: runs web searches for each `WebSearchItem.query` and returns a 2–3 paragraph summary under 300 words.

- **`WriterAgent` (`Agents/writer_agent.py`)**
  - Input: original query + summarized search results
  - Output: `ReportData` (`short_summary`, `markdown_report`, `follow_up_questions`)
  - Handoff: calls `EvaluatorAgent` for validation; will rewrite if needed.

- **`EvaluatorAgent` (`Agents/evaluator_agent.py`)**
  - Output type: `EvaluationModel` (`valid`, `reason`)
  - Criteria: relevance, factual accuracy, clarity, completeness, presence of required fields.
  - If invalid: hands back to `WriterAgent` with guidance.

- **`Email agent` (`Agents/email_agent.py`)**
  - Tools: `send_email(subject, html_body)` → uses SendGrid API
  - Task: transform markdown → HTML, craft subject line, send email.

---