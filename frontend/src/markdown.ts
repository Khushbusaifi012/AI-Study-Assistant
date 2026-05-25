/** Minimal markdown → HTML for tutor replies */
export function renderMarkdown(text: string): string {
  let html = escapeHtml(text);

  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");

  const lines = html.split("\n");
  const out: string[] = [];
  let inTable = false;

  for (const line of lines) {
    if (line.startsWith("|") && line.includes("|")) {
      if (!inTable) {
        inTable = true;
        out.push("<table>");
      }
      if (/^\|[\s\-:|]+\|$/.test(line)) continue;
      const cells = line
        .slice(1, -1)
        .split("|")
        .map((c) => `<td>${c.trim()}</td>`)
        .join("");
      out.push(`<tr>${cells}</tr>`);
      continue;
    }
    if (inTable) {
      out.push("</table>");
      inTable = false;
    }
    if (line.startsWith("- ")) {
      out.push(`<li>${line.slice(2)}</li>`);
    } else if (line.trim() === "---") {
      out.push("<hr />");
    } else if (line.trim()) {
      out.push(`<p>${line}</p>`);
    }
  }
  if (inTable) out.push("</table>");

  return out.join("\n").replace(/(<li>[\s\S]*?<\/li>)+/g, (m) => `<ul>${m}</ul>`);
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
