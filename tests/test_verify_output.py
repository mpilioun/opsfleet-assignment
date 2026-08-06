from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent.tools.verify_output import VerifyResult, verify_output


def _fake_runtime() -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1")


@patch("src.agent.tools.verify_output.get_llm_model")
async def test_verify_output_passes(mock_get_llm_model):
    judge = MagicMock()
    judge.ainvoke = AsyncMock(return_value=VerifyResult(passed=True))
    mock_get_llm_model.return_value.with_structured_output.return_value = judge

    result = await verify_output.coroutine(
        question="Top customers?", draft_report="Here they are.", runtime=_fake_runtime()
    )

    assert result.status == "success"


@patch("src.agent.tools.verify_output.get_llm_model")
async def test_verify_output_reports_issues(mock_get_llm_model):
    judge = MagicMock()
    judge.ainvoke = AsyncMock(
        return_value=VerifyResult(passed=False, issues=["Includes a raw email address"])
    )
    mock_get_llm_model.return_value.with_structured_output.return_value = judge

    result = await verify_output.coroutine(
        question="Top customers?", draft_report="Contact john@x.com", runtime=_fake_runtime()
    )

    assert result.status == "error"
    assert "email address" in result.content


@patch("src.agent.tools.verify_output.get_llm_model")
async def test_verify_output_handles_judge_failure(mock_get_llm_model):
    judge = MagicMock()
    judge.ainvoke = AsyncMock(side_effect=RuntimeError("rate limited"))
    mock_get_llm_model.return_value.with_structured_output.return_value = judge

    result = await verify_output.coroutine(
        question="Top customers?", draft_report="Here they are.", runtime=_fake_runtime()
    )

    assert result.status == "error"
    assert "auto-verified" in result.content
