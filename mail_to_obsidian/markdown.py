import re

from markdownify import markdownify as md


def clean_filename(filename: str) -> str:
    value = filename.strip() or "email"
    safe_name = re.sub(r"[^\w\-. ]+", "_", value)
    return safe_name[:250]


def html_to_markdown(html_content: str) -> tuple[str, str]:
    html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
    markdown_text = md(html_content, heading_style="ATX")
    markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text).strip()

    title_match = re.search(r"^#\s*(.+)$", markdown_text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ""
    return markdown_text, title
