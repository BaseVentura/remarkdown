# Mail to Obsidian

This package fetches GMX emails and saves them as Markdown files suitable for Obsidian.

## Local setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the dependency:

```bash
python -m pip install -r requirements.txt
```

3. Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

4. Edit `.env` with your GMX settings:

```text
GMX_EMAIL_USERNAME=your_email@gmx.com
GMX_EMAIL_PASSWORD=your_password
GMX_EMAIL_SUBFOLDER=INBOX
GMX_EMAIL_OUTPUT_DIR=./emails
GMX_EMAIL_SENDER_FILTER=my@remarkable.com
```

## Project structure

- `mail_to_obsidian/` — package source code
- `run.py` — root wrapper script
- `pyproject.toml` — package metadata and CLI entry
- `requirements.txt` — runtime dependency list
- `scripts/legacy_gmx_email_retrieval.py` — original script preserved for comparison
- `.env.example` — environment variable template

## Usage

Run the package entrypoint:

```bash
python -m mail_to_obsidian
```

Or use the wrapper script:

```bash
python run.py
```

Override settings with CLI options:

```bash
python -m mail_to_obsidian --username your_email@gmx.com --password your_password
```

## Extending the project

- Add new email processing logic in `mail_to_obsidian/imap_client.py`
- Keep markdown conversion in `mail_to_obsidian/markdown.py`
- Add configuration or env helpers in `mail_to_obsidian/config.py`
- Change CLI options in `mail_to_obsidian/cli.py`

If you return to this project later, first activate the virtual environment:

```bash
source .venv/bin/activate
```

## TODO

- Remove the legacy script after testing
- Test the package itself and remove the old version
- Add better error handling for IMAP login and parsing
