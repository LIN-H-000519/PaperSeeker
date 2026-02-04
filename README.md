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

Add your API credentials:
- `PARATERA_API_KEY` - LLM API key (for AI filtering and summarization)
- `EMAIL_PASSWORD` - Email app password

### 3. Configure Settings

```bash
# Copy config template
cp config.example.yaml config.yaml

# Edit config
nano config.yaml
```

Configure email server and search parameters.

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
# Run once immediately (search last 3 days)
python main.py --run-once

# Specify date range
python main.py --run-once --from-date 2025-01-01 --to-date 2025-01-15

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

## LLM Configuration

```yaml
llm:
  provider: "openai"  # OpenAI-compatible client
  model: "Qwen3-Coder-480B-A35B-Instruct"
  api_key: "${PARATERA_API_KEY}"
  base_url: "https://llmapi.paratera.com/v1/"
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
python main.py --run-once                # Run immediately
python main.py --run-once --from-date 2025-01-01 --to-date 2025-01-15
python main.py --send-test-email         # Send test email
```

## Supported Email Providers

Configure in `config.yaml`:

```yaml
# Gmail
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
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
