from langchain_core.messages import AIMessage, HumanMessage

from scripts.eval_golden import _final_report_text


def test_final_report_text_returns_last_ai_message():
    result = {
        "messages": [
            HumanMessage(content="question"),
            AIMessage(content="first draft"),
            AIMessage(content="final report"),
        ]
    }

    assert _final_report_text(result) == "final report"


def test_final_report_text_skips_empty_ai_messages():
    result = {
        "messages": [
            AIMessage(content="final report"),
            AIMessage(content=""),
        ]
    }

    assert _final_report_text(result) == "final report"


def test_final_report_text_returns_empty_string_when_no_ai_message():
    assert _final_report_text({"messages": [HumanMessage(content="question")]}) == ""
