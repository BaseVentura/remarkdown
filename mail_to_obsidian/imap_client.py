import email
import imaplib
from email import policy
from email.message import Message
from pathlib import Path
from typing import Optional

from .config import Config
from .markdown import clean_filename


IMAP_SERVER = "imap.gmx.com"
IMAP_PORT = 993


def decode_header_value(value: Optional[str]) -> str:
    if not value:
        return ""
    from email.header import decode_header, make_header

    return str(make_header(decode_header(value)))


def extract_message_body(message: Message) -> tuple[str, str]:
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
        from .markdown import html_to_markdown

        return html_to_markdown(html_part)

    body = text_part.strip() if text_part else ""
    return body, ""


def fetch_emails(config: Config) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    try:
        mail.login(config.username, config.password)

        status, _ = mail.select(config.subfolder, readonly=True)
        if status != "OK":
            raise RuntimeError(f"Unable to select folder: {config.subfolder}")

        status, data = mail.search(None, "FROM", f'"{config.sender_filter}"')
        if status != "OK":
            raise RuntimeError("IMAP search failed")

        message_ids = data[0].split()
        if not message_ids:
            print(f"No messages found in {config.subfolder} from {config.sender_filter}")
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

                    output_file = config.output_dir / f"{safe_name}.md"
                    output_file.write_text(markdown_content, encoding="utf-8")
                    print(f"Saved email: {output_file}")
    finally:
        mail.close()
        mail.logout()
