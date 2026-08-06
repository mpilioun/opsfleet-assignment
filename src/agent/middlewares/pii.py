"""Layer 2 PII backstop (layer 1 is src/safety/sql_guard.py blocking PII columns at
the SQL level). Catches structural PII (email/phone/credit-card/IP patterns) that
might leak into generated prose, scanning both tool results and the final answer.
Uses langchain's built-in PIIMiddleware - reuse over hand-rolled regex scrubbing.
"""

from langchain.agents.middleware import PIIMiddleware

# A pattern string, not a compiled re.Pattern: PIIMiddleware's detector resolver
# only special-cases str (compiles it itself) or a callable - a pre-compiled
# Pattern falls through to the "custom callable" branch and is called directly,
# which raises (a Pattern object isn't callable).
PHONE_NUMBER_PATTERN = r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"

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
        detector=PHONE_NUMBER_PATTERN,
        strategy="redact",
        apply_to_tool_results=True,
        apply_to_output=True,
    ),
]
