# PaperSeeker

AI-Powered Academic Paper Recommendation System

## Overview

PaperSeeker automatically searches for relevant academic papers from [OpenAlex](https://openalex.org), uses LLM to intelligently filter relevance, and delivers curated papers via email.

## Features

- **OpenAlex Integration** - Free, high-quality academic paper database
- **AI-Powered Filtering** - Uses LLM to score and filter relevant papers
- **Bilingual Summaries** - Auto-generates Chinese and English abstracts
- **Scheduled Delivery** - Daily automated email delivery
- **Fully Configurable** - Easy to customize research interests and prompts
- **Cost-Effective** - Keyword pre-filtering + LLM refinement

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
notepad .env
```

Configure your API credentials in `.env`:
- `API_KEY` - LLM API key (get from [Paratera](https://www.paratera.com/llm-api) or [DeepSeek](https://platform.deepseek.com))
- `EMAIL_PASSWORD` - Email app password
  - **Gmail**: Enable 2FA first, then get app password at https://myaccount.google.com/apppasswords
  - **163 Mail**: Enable IMAP in settings, get authorization code at https://mail.163.com/settings/index

### 3. Configure Settings

```bash
# Copy config template
cp config.example.yaml config.yaml

# Edit config
nano config.yaml
```

Configure email server and LLM parameters.

### 4. Define Research Interests

```bash
nano prompts.yaml
```

Modify `research_keywords` to match your research focus.

### 5. Run Test

```bash
python -m tests.test_paper_flow
```

### 6. Start Service

```bash
# Run once immediately (search yesterday)
python main.py --run-once

# Specify date range (search 1 day)
python main.py --run-once --from-date 2025-01-14 --to-date 2025-01-14

# Start scheduled delivery
python main.py
```

## Project Structure

```
PaperSeeker/
├── config.yaml              # Config file (sensitive, not committed)
├── prompts.yaml             # User-editable prompts and keywords
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── paper_searcher.py   # OpenAlex paper search
│   ├── paper_filter.py     # Keyword pre-filter + LLM refinement
│   ├── summarizer.py       # Bilingual summary generation
│   ├── email_sender.py     # Email delivery
│   └── scheduler.py        # Scheduled tasks
├── tests/
│   └── test_paper_flow.py
├── main.py                 # Entry point
└── README.md
```

## Configuration

All configurable settings are in `config.yaml`:

```yaml
# LLM API Configuration
llm:
  provider: "openai"        # OpenAI-compatible client
  model: "DeepSeek-V3.2"   # Update to your preferred model
  api_key: "${API_KEY}"     # Read from .env
  base_url: "https://llmapi.paratera.com/v1/"  # Update for your API provider

# Email Configuration
email:
  smtp_server: "smtp.gmail.com"   # or "smtp.163.com"
  smtp_port: 587                   # 25 for 163 mail
  sender_email: "your-email@domain.com"
  sender_password: "${EMAIL_PASSWORD}"
  recipient_email: "recipient@example.com"

# Search Configuration
search:
  max_results: 20          # Papers per keyword
  days_back: 1             # Search recent N days
  relevance_threshold: 3   # Minimum relevance score (1-5)

# Scheduler Configuration
scheduler:
  trigger_time: "21:00"   # UTC time (22:00 UTC = 06:00 Beijing Time)
  enabled: true
```

## Filtering Strategy (Cost Optimization)

1. **Pre-filter (Free)**: Keyword matching
   - Uses `research_keywords` from `prompts.yaml`
   - Quickly filters out irrelevant papers

2. **Refinement (Paid)**: LLM API
   - Only calls API for pre-filtered candidates
   - Scores 1-5, keeps papers with score >= 4

## CLI Options

```bash
python main.py --test                    # Run tests
python main.py --run-once               # Run immediately (yesterday)
python main.py --run-once --from-date 2025-01-14 --to-date 2025-01-14
python main.py --send-test-email         # Send test email
```

## Email Providers

Configure in `config.yaml`:

```yaml
# Gmail
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587

# 163 Mail
email:
  smtp_server: "smtp.163.com"
  smtp_port: 25
```

## GitHub Actions Setup (Automated Daily Push)

1. **Fork or clone this repository**

2. **Add secrets** in Repository Settings → Secrets and variables → Actions:
   - `API_KEY` - Your LLM API key
   - `EMAIL_PASSWORD` - Your email app password

3. **The workflow runs daily at UTC 22:00** (Beijing Time 06:00+1)

4. **To test manually**:
   - Go to Repository → Actions → "PaperSeeker Daily Push"
   - Click "Run workflow"

5. **To modify schedule**, edit `.github/workflows/workflow.yml`:
   ```yaml
   schedule:
     - cron: '0 22 * * *'  # Change to your preferred UTC time
   ```

## Dependencies

```
openalex>=0.5.0
openai>=1.0.0
apscheduler==3.10.4
pyyaml==6.0.1
python-dotenv==1.0.0
tqdm>=4.66.0
```

## License

MIT
