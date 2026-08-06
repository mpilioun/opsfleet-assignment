from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.agent.tools.verify_output import VerifyResult, verify_output


def _fake_runtime() -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1")


@patch("src.agent.tools.verify_output.run_structured", new_callable=AsyncMock)
async def test_verify_output_passes(mock_run_structured):
    mock_run_structured.return_value = VerifyResult(passed=True)

    result = await verify_output.coroutine(
        question="Top customers?", draft_report="Here they are.", runtime=_fake_runtime()
    )

    assert result.status == "success"


@patch("src.agent.tools.verify_output.run_structured", new_callable=AsyncMock)
async def test_verify_output_reports_issues(mock_run_structured):
    mock_run_structured.return_value = VerifyResult(
        passed=False, issues=["Includes a raw email address"]
    )

    result = await verify_output.coroutine(
        question="Top customers?", draft_report="Contact john@x.com", runtime=_fake_runtime()
    )

    assert result.status == "error"
    assert "email address" in result.content


@patch("src.agent.tools.verify_output.run_structured", new_callable=AsyncMock)
async def test_verify_output_handles_judge_failure(mock_run_structured):
    mock_run_structured.side_effect = RuntimeError("rate limited")

    result = await verify_output.coroutine(
        question="Top customers?", draft_report="Here they are.", runtime=_fake_runtime()
    )

    assert result.status == "error"
    assert "auto-verified" in result.content
