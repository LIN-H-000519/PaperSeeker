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

Configure all API credentials in `.env`:
- `API_KEY` - Your LLM API key
- `LLM_MODEL` - LLM model name (e.g., DeepSeek-V3.2)
- `LLM_BASE_URL` - API endpoint URL
- `EMAIL_PASSWORD` - Email app password (Gmail/163)
- `SENDER_EMAIL` - Your email address
- `RECIPIENT_EMAIL` - Recipient email address
- `SMTP_SERVER` / `SMTP_PORT` - Email server settings

### 3. Configure Settings

```bash
# Copy config template
cp config.example.yaml config.yaml

# Edit config
nano config.yaml
```

Configure search and scheduler settings.

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
├── config.yaml              # Search & scheduler config (not committed)
├── prompts.yaml             # User-editable prompts and keywords
├── requirements.txt         # Dependencies
├── .env.example            # Environment template (fill in your credentials)
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

### Environment Variables (`.env`)

All sensitive credentials and API configurations are in `.env`:

```bash
# LLM API Configuration
API_KEY=your-api-key
LLM_MODEL=DeepSeek-V3.2
LLM_BASE_URL=https://llmapi.paratera.com/v1/

# Email Configuration
EMAIL_PASSWORD=your-app-password
SENDER_EMAIL=your-email@domain.com
RECIPIENT_EMAIL=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Search Settings (`config.yaml`)

```yaml
search:
  max_results: 20          # Papers per keyword
  days_back: 1             # Search recent N days
  relevance_threshold: 3   # Minimum LLM score (1-5)

scheduler:
  trigger_time: "21:00"   # UTC time for local scheduler
  enabled: true
```

## Email Providers

Configure SMTP settings in `.env`:

```bash
# Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# 163 Mail
SMTP_SERVER=smtp.163.com
SMTP_PORT=25
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
