"""Layer 2 PII backstop (layer 1 is src/safety/sql_guard.py blocking PII columns at
the SQL level). Catches structural PII (email/phone/credit-card/IP patterns) that
might leak into generated prose, scanning both tool results and the final answer.
Uses langchain's built-in PIIMiddleware - reuse over hand-rolled regex scrubbing.
"""

import re

from langchain.agents.middleware import PIIMiddleware

PHONE_NUMBER_REGEX = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

PII_MIDDLEWARE = [
    PIIMiddleware(
        "email", strategy="redact", apply_to_tool_results=True, apply_to_output=True
    ),
    PIIMiddleware(
        "credit_card",
        strategy="redact",
        apply_to_tool_results=True,
        apply_to_output=True,
    ),
    PIIMiddleware(
        "ip", strategy="redact", apply_to_tool_results=True, apply_to_output=True
    ),
    PIIMiddleware(
        "phone_number",
        detector=PHONE_NUMBER_REGEX,
        strategy="redact",
        apply_to_tool_results=True,
        apply_to_output=True,
    ),
]
