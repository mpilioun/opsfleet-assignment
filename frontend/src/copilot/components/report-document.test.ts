import { describe, expect, it } from "vitest";

import { formatSize, slugify, splitReportResult } from "./report-document";

describe("slugify", () => {
  it("makes a filename-safe slug", () => {
    expect(slugify("Q3 Sales & Inventory Review")).toBe("q3-sales-inventory-review");
  });

  it("falls back to 'report' when nothing survives", () => {
    expect(slugify("!!!")).toBe("report");
  });

  it("caps the length", () => {
    expect(slugify("a".repeat(200)).length).toBe(60);
  });
});

describe("splitReportResult", () => {
  it("pulls the title out of the leading h1 that read_report emits", () => {
    const result = "# Weekly Sales\n(saved 2026-08-07T10:00:00+00:00)\n\nRevenue is up.";
    expect(splitReportResult(result)).toEqual({
      title: "Weekly Sales",
      content: "(saved 2026-08-07T10:00:00+00:00)\n\nRevenue is up.",
    });
  });

  it("is null for a result that is not a report, so failures never render as a document", () => {
    expect(splitReportResult("No saved report with id abc.")).toBeNull();
    expect(splitReportResult("# \nempty title")).toBeNull();
  });
});

describe("formatSize", () => {
  it("measures UTF-8 bytes, not UTF-16 code units", () => {
    expect(formatSize("a".repeat(2048))).toBe("2.0 KB");
    expect(formatSize("€".repeat(1024))).toBe("3.0 KB");
  });
});
