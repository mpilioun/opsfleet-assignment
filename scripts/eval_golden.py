"""Offline QA eval: replay each golden-bucket seed question through the live
agent and score the resulting report with an LLM judge against the seed's
human-written report (a loose rubric - "does this cover the same ground and
stay grounded/PII-free", not a wording match).

Manual smoke-eval, same spirit as probe_llm.py/probe_bq.py - not part of the
pytest suite since it needs a running Postgres, a Gemini API key, and live
BigQuery access. Run via `make eval-golden`.
"""

import asyncio
import uuid

from langchain_core.messages import AIMessage, HumanMessage

from src.agent.agent import build_agent
from src.agent.golden_bucket import SEED_TRIOS
from src.agent.structured_llm import run_structured
from src.agent.tools.verify_output import VerifyResult
from src.database.postgres_manager import postgres_manager

JUDGE_SYSTEM_PROMPT = (
    "You are a strict QA reviewer for a retail data-analysis agent. Given the "
    "ORIGINAL QUESTION, a REFERENCE REPORT written by a human analyst, and a DRAFT "
    "REPORT produced by the agent, decide whether the draft covers the same "
    "substantive ground as the reference (not matching wording), stays grounded "
    "in real data with no fabricated numbers, and contains no PII (customer "
    "names, emails, phone numbers, street addresses). List concrete issues if it "
    "fails."
)


def _final_report_text(result: dict) -> str:
    messages = result.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            return message.content
    return ""


async def _run_one(agent, trio: dict) -> VerifyResult:
    thread_id = f"eval-{uuid.uuid4()}"
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=trio["question"])]},
        config={"configurable": {"thread_id": thread_id, "user_id": "eval-golden"}},
    )
    draft_report = _final_report_text(result)

    return await run_structured(
        system_prompt=JUDGE_SYSTEM_PROMPT,
        user_content=(
            f"ORIGINAL QUESTION:\n{trio['question']}\n\n"
            f"REFERENCE REPORT:\n{trio['report']}\n\n"
            f"DRAFT REPORT:\n{draft_report or '(agent returned no report)'}"
        ),
        response_format=VerifyResult,
    )


async def main() -> None:
    await postgres_manager.initialize()
    agent = build_agent()

    passed = 0
    for trio in SEED_TRIOS:
        judged = await _run_one(agent, trio)
        status = "PASS" if judged.passed else "FAIL"
        passed += judged.passed
        print(f"[{status}] {trio['id']}: {trio['question']}")
        if not judged.passed:
            for issue in judged.issues:
                print(f"    - {issue}")

    total = len(SEED_TRIOS)
    print(f"\n{passed}/{total} passed ({passed / total:.0%})")

    await postgres_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
