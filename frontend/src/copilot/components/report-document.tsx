import { Markdown } from "@copilotkit/react-ui";

/** Filename-safe slug for the download attribute. */
export const slugify = (title: string): string =>
  title
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60) || "report";

/** `read_report` returns "# <title>\n(saved <ts>)\n\n<body>" (see read_report.py),
 *  so the title is recovered from the leading h1 to label the document card.
 *  Null for anything without that h1 - a failure string is not a document. */
export const splitReportResult = (
  result: string,
): { title: string; content: string } | null => {
  const [head, ...rest] = result.split("\n");
  if (!head.startsWith("# ")) return null;
  const title = head.slice(2).trim();
  return title ? { title, content: rest.join("\n").trim() } : null;
};

/** UTF-8 size, matching the bytes the download actually writes. */
export const formatSize = (content: string): string =>
  `${(new TextEncoder().encode(content).length / 1024).toFixed(1)} KB`;

/** A saved report shown as a collapsible attachment: filename chip, rendered
 *  markdown preview, and a download of the raw `.md`. */
export const ReportDocument: React.FC<{
  title: string;
  content: string;
  streaming?: boolean;
}> = ({ title, content, streaming = false }) => {
  const filename = `${slugify(title)}.md`;

  return (
    <div className="report-doc">
      {/* ponytail: <details> gives expand/collapse for free - no open/close state. */}
      <details>
        <summary className="report-doc-summary">
          <span aria-hidden="true">📄</span>
          <span className="report-doc-name">{filename}</span>
          <span className="report-doc-meta">{streaming ? "writing…" : formatSize(content)}</span>
        </summary>
        <div className="report-doc-body">{content && <Markdown content={content} />}</div>
      </details>
      {!streaming && content && (
        // ponytail: data: URL keeps this stateless - no createObjectURL to revoke.
        // Reports are a few KB; switch to a Blob URL if they ever grow past ~1 MB.
        <a
          className="btn btn-secondary report-doc-download"
          href={`data:text/markdown;charset=utf-8,${encodeURIComponent(content)}`}
          download={filename}
        >
          Download
        </a>
      )}
    </div>
  );
};
