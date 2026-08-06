from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.agent.structured_llm import run_structured
from src.observability.logging import get_logger

logger = get_logger(__name__)

JUDGE_SYSTEM_PROMPT = (
    "You are a strict QA reviewer for a data-analysis report written for a retail "
    "executive. Given the ORIGINAL QUESTION and the DRAFT REPORT, decide whether the "
    "draft actually answers the question, stays grounded in data that was actually "
    "provided (no fabricated numbers), and contains no PII (customer names, emails, "
    "phone numbers, street addresses). List concrete issues if it fails."
)


class VerifyResult(BaseModel):
    passed: bool
    issues: list[str] = Field(default_factory=list)


@tool
async def verify_output(
    question: str, draft_report: str, runtime: ToolRuntime
) -> ToolMessage:
    """LLM-judge self-check: verify a draft report actually answers the original
    question, is grounded in real data, and leaks no PII. Call this before
    presenting a final report to the user.
    """
    logger.info("Agent Called Tool", extra={"tool_name": "verify_output"})
    try:
        result = await run_structured(
            system_prompt=JUDGE_SYSTEM_PROMPT,
            user_content=f"ORIGINAL QUESTION:\n{question}\n\nDRAFT REPORT:\n{draft_report}",
            response_format=VerifyResult,
        )
    except Exception as exc:  # noqa: BLE001 - tool boundary: never raise, always return a ToolMessage
        return ToolMessage(
            content=f"Verification could not run ({exc}); present the report with a note that it wasn't auto-verified.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    if result.passed:
        return ToolMessage(
            content="Verification passed.", tool_call_id=runtime.tool_call_id
        )
    return ToolMessage(
        content="Verification found issues:\n"
        + "\n".join(f"- {issue}" for issue in result.issues),
        status="error",
        tool_call_id=runtime.tool_call_id,
    )
