import argparse
from pathlib import Path

from .config import Config, DEFAULT_SENDER_FILTER, get_env, load_dotenv
from .imap_client import fetch_emails


def parse_args() -> argparse.Namespace:
    parser = ArgumentParser(description="Fetch GMX emails and save them as Markdown files")
    parser.add_argument("--username", default=get_env("GMX_EMAIL_USERNAME"), help="GMX username/email")
    parser.add_argument("--password", default=get_env("GMX_EMAIL_PASSWORD"), help="GMX password")
    parser.add_argument("--subfolder", default=get_env("GMX_EMAIL_SUBFOLDER", "INBOX"), help="IMAP subfolder to read")
    parser.add_argument("--output-dir", default=get_env("GMX_EMAIL_OUTPUT_DIR", "."), help="Directory where markdown files are saved")
    parser.add_argument("--sender-filter", default=get_env("GMX_EMAIL_SENDER_FILTER", DEFAULT_SENDER_FILTER), help="Filter emails by sender address")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    if not args.username or not args.password:
        raise SystemExit(
            "Missing GMX username/password. Set GMX_EMAIL_USERNAME and GMX_EMAIL_PASSWORD in the environment or .env file, or pass --username/--password."
        )

    config = Config(
        username=args.username,
        password=args.password,
        subfolder=args.subfolder,
        output_dir=Path(args.output_dir).expanduser(),
        sender_filter=args.sender_filter,
    )

    fetch_emails(config)
