from pydantic import BaseModel, Field


class DataAnalystResult(BaseModel):
    """Structured terminal output of the data-analyst subagent."""

    findings: str = Field(
        description="Aggregated, non-PII analysis findings for the report-writer to turn into a report."
    )
    sql_used: str = Field(
        default="",
        description="The final SQL query that produced these findings, if any.",
    )


class ReportWriterResult(BaseModel):
    """Structured terminal output of the report-writer subagent."""

    report: str = Field(description="The final report/answer text to show the user.")
    chart_path: str | None = Field(
        default=None, description="Path to a generated chart image, if one was created."
    )
