#!/usr/bin/env python3
from __future__ import annotations

import argparse
import email
import imaplib
import os
import re
from email import policy
from email.header import decode_header, make_header
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Tuple

from markdownify import markdownify as md

IMAP_SERVER = "imap.gmx.com"
IMAP_PORT = 993
DEFAULT_SENDER_FILTER = "my@remarkable.com"


def clean_filename(filename: str) -> str:
    value = filename.strip() or "email"
    safe_name = re.sub(r"[^\w\-. ]+", "_", value)
    return safe_name[:250]


def decode_header_value(value: Optional[str]) -> str:
    if not value:
        return ""
    return str(make_header(decode_header(value)))


def html_to_markdown(html_content: str) -> Tuple[str, str]:
    html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
    markdown_text = md(html_content, heading_style="ATX")
    markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text).strip()

    title_match = re.search(r"^#\s*(.+)$", markdown_text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ""
    return markdown_text, title


def extract_message_body(message: EmailMessage) -> Tuple[str, str]:
    html_part = None
    text_part = None

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue

            content_type = part.get_content_type()
            if content_type == "text/html" and html_part is None:
                html_part = part.get_content()
            elif content_type == "text/plain" and text_part is None:
                text_part = part.get_content()
    else:
        content_type = message.get_content_type()
        if content_type == "text/html":
            html_part = message.get_content()
        elif content_type == "text/plain":
            text_part = message.get_content()

    if html_part:
        return html_to_markdown(html_part)

    body = text_part.strip() if text_part else ""
    return body, ""


def fetch_emails(
    username: str,
    password: str,
    subfolder: str,
    output_dir: Path,
    sender_filter: str = DEFAULT_SENDER_FILTER,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    try:
        mail.login(username, password)

        status, _ = mail.select(subfolder, readonly=True)
        if status != "OK":
            raise RuntimeError(f"Unable to select folder: {subfolder}")

        status, data = mail.search(None, "FROM", f'"{sender_filter}"')
        if status != "OK":
            raise RuntimeError("IMAP search failed")

        message_ids = data[0].split()
        if not message_ids:
            print(f"No messages found in {subfolder} from {sender_filter}")
            return

        for message_id in message_ids:
            status, data = mail.fetch(message_id, "(RFC822)")
            if status != "OK":
                print(f"Failed to fetch message {message_id.decode()}")
                continue

            for response_part in data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    message = email.message_from_bytes(raw_email, policy=policy.default)

                    subject = decode_header_value(message["Subject"])
                    date = message["Date"] or ""

                    body, title = extract_message_body(message)
                    title = title or subject or date
                    safe_name = clean_filename(title)

                    markdown_content = f"""---
Date: {date}
Subject: {subject}
---

{body}
"""

                    output_file = output_dir / f"{safe_name}.md"
                    output_file.write_text(markdown_content, encoding="utf-8")
                    print(f"Saved email: {output_file}")
    finally:
        mail.close()
        mail.logout()


def load_dotenv(dotenv_path: Path = Path(".env")) -> None:
    if not dotenv_path.exists():
        return

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_env_default(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GMX emails and save them as Markdown files")
    parser.add_argument("--username", default=get_env_default("GMX_EMAIL_USERNAME"), help="GMX username/email")
    parser.add_argument("--password", default=get_env_default("GMX_EMAIL_PASSWORD"), help="GMX password")
    parser.add_argument("--subfolder", default=get_env_default("GMX_EMAIL_SUBFOLDER", "INBOX"), help="IMAP subfolder to read")
    parser.add_argument("--output-dir", default=get_env_default("GMX_EMAIL_OUTPUT_DIR", "."), help="Directory where markdown files are saved")
    parser.add_argument("--sender-filter", default=get_env_default("GMX_EMAIL_SENDER_FILTER", DEFAULT_SENDER_FILTER), help="Filter emails by sender address")
    return parser.parse_args()


if __name__ == "__main__":
    load_dotenv()
    args = parse_args()

    if not args.username or not args.password:
        raise SystemExit("Missing GMX username/password. Set GMX_EMAIL_USERNAME and GMX_EMAIL_PASSWORD in the environment or .env file, or pass --username/--password.")

    fetch_emails(
        username=args.username,
        password=args.password,
        subfolder=args.subfolder,
        output_dir=Path(args.output_dir).expanduser(),
        sender_filter=args.sender_filter,
    )
