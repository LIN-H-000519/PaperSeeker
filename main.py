"""
PaperSeeker - AI-Powered Academic Paper Recommendation System
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_config
from src.paper_searcher import OpenAlexSearcher
from src.paper_filter import PaperFilter, KeywordFilter
from src.summarizer import AbstractSummarizer
from src.email_sender import EmailSender
from src.scheduler import PaperScheduler


def daily_task(from_date: str = None, to_date: str = None, days_back: int = None):
    """
    Daily paper push task

    Args:
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        days_back: Search recent N days
    """
    # Load configuration
    config = get_config()

    # Test email connection
    print(f"\n[PaperSeeker] Testing email server connection...")
    email_sender = EmailSender(config)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((config.smtp_server, config.smtp_port))
        sock.close()
        print(f"[PaperSeeker] Email server is reachable.")
    except Exception as e:
        print(f"[PaperSeeker] Email connection failed: {e}")
        print("[PaperSeeker] Aborting task. Please check your network or SMTP settings.")
        return

    print(f"\n[PaperSeeker] Starting daily paper search...")
    print(f"[PaperSeeker] Keywords: {config.research_keywords[:3]}...")

    # Search papers
    searcher = OpenAlexSearcher(api_url=config.openalex_api_url)
    papers = searcher.search(
        keywords=config.research_keywords,
        exclude_keywords=config.exclude_keywords,
        days_back=days_back or config.days_back,
        max_results=config.max_results,
        from_date=from_date or config.from_date,
        to_date=to_date or config.to_date,
    )

    if not papers:
        print("[PaperSeeker] No papers found today.")
        return

    print(f"\n[PaperSeeker] Found {len(papers)} papers, filtering...")

    # Filter papers (keyword pre-filter + AI refinement)
    if config.llm_api_key:
        print("[PaperSeeker] Using AI filter...")
        filter_prompt = config.filter_prompt
        ai_filter = PaperFilter(
            provider=config.llm_provider,
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            filter_prompt=filter_prompt,
        )

        # Quick keyword filter
        keyword_filter = KeywordFilter(
            keywords=config.research_keywords,
            exclude_keywords=config.exclude_keywords,
        )
        candidates = keyword_filter.filter_batch(papers, threshold=1, show_progress=False)
        print(f"  After keyword filter: {len(candidates)} candidates")

        # AI refinement
        filtered_papers = ai_filter.filter_batch(
            candidates,
            threshold=config.relevance_threshold,
            show_progress=True,
        )
    else:
        print("[PaperSeeker] Using keyword filter (no API key)...")
        keyword_filter = KeywordFilter(
            keywords=config.research_keywords,
            exclude_keywords=config.exclude_keywords,
        )
        filtered_papers = keyword_filter.filter_batch(
            papers,
            threshold=config.relevance_threshold,
            show_progress=True,
        )

    if not filtered_papers:
        print("\n[PaperSeeker] No relevant papers found today, sending notification email...")
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        email_sender = EmailSender(config)
        email_sender.send_empty_result(date_str)
        return

    print(f"\n[PaperSeeker] {len(filtered_papers)} relevant papers, generating summaries...")

    # Generate summaries (only for high-score papers)
    summarize_threshold = config.summarize_threshold
    papers_for_summary = [p for p in filtered_papers if p.get("relevance_score", 0) >= summarize_threshold]
    papers_without_summary = [p for p in filtered_papers if p.get("relevance_score", 0) < summarize_threshold]

    print(f"[PaperSeeker] Threshold: {summarize_threshold}, Papers for summary: {len(papers_for_summary)}, Without summary: {len(papers_without_summary)}")

    papers_with_summary = []

    if config.llm_api_key:
        summarizer = AbstractSummarizer(
            provider=config.llm_provider,
            model=config.llm_model,
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            summarize_prompt=config.summarize_prompt,
        )
        if papers_for_summary:
            summarized = summarizer.summarize_batch(
                papers_for_summary,
                show_progress=True,
            )
            papers_with_summary.extend(summarized)

        # Low-score papers without summary
        for paper in papers_without_summary:
            paper["summary_zh"] = "（相关性较低，仅保留基本信息）"
            paper["summary_en"] = "(Low relevance, basic info only)"
            papers_with_summary.append(paper)
    else:
        # No API key, use original abstract
        for paper in filtered_papers:
            paper["summary_zh"] = paper.get("abstract", "")[:300] + "..."
            paper["summary_en"] = "(No English summary available)"
        papers_with_summary = filtered_papers

    # Send email
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n[PaperSeeker] Sending email for {len(papers_with_summary)} papers...")

    email_sender = EmailSender(config)
    success = email_sender.send(papers_with_summary, date_str)

    if success:
        print(f"\n[PaperSeeker] Daily task completed! {len(papers_with_summary)} papers sent.")
    else:
        print(f"\n[PaperSeeker] Email sending failed.")


def run_test():
    """Run test flow"""
    print("\n" + "=" * 60)
    print("PaperSeeker Test Mode")
    print("=" * 60 + "\n")

    config = get_config()
    print("[Test] Configuration loaded successfully")

    # Test search
    print("\n[Test] Testing OpenAlex search...")
    searcher = OpenAlexSearcher()
    test_papers = searcher.search(
        keywords=config.research_keywords[:2],
        days_back=7,
        max_results=5,
        verbose=True,
    )
    print(f"[Test] Found {len(test_papers)} test papers")

    if test_papers:
        # Test filter
        print("\n[Test] Testing filter...")
        keyword_filter = KeywordFilter(
            keywords=config.research_keywords,
            exclude_keywords=config.exclude_keywords,
        )
        filtered = keyword_filter.filter_batch(test_papers, threshold=3, show_progress=True)
        print(f"[Test] Filtered to {len(filtered)} relevant papers")

        if filtered and config.llm_api_key:
            # Test AI filter
            print("\n[Test] Testing AI filter...")
            ai_filter = PaperFilter(
                provider=config.llm_provider,
                model=config.llm_model,
                api_key=config.llm_api_key,
                base_url=config.llm_base_url,
                filter_prompt=config.filter_prompt,
            )
            for paper in test_papers[:2]:
                result = ai_filter.filter_single(
                    title=paper.get("title", ""),
                    abstract=paper.get("abstract", ""),
                )
                print(f"  Score: {result['score']}, Reason: {result['reason']}")

        # Test email sender
        print("\n[Test] Testing email sender...")
        email_sender = EmailSender(config)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="PaperSeeker - AI Paper Tracker")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--run-once", action="store_true", help="Run once immediately")
    parser.add_argument("--send-test-email", action="store_true", help="Send test email")
    parser.add_argument("--config", type=str, help="Config file path")
    parser.add_argument("--prompts", type=str, help="Prompts file path")
    parser.add_argument("--from-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--days-back", type=int, help="Search recent N days")

    args = parser.parse_args()

    # Load configuration
    config = get_config(args.config, args.prompts)

    # Send test email
    if args.send_test_email:
        email_sender = EmailSender(config)
        if email_sender.send_test():
            print("Test email sent successfully!")
        else:
            print("Failed to send test email.")
        return

    # Run test mode
    if args.test:
        run_test()
        return

    # Run once
    if args.run_once:
        daily_task(
            from_date=args.from_date,
            to_date=args.to_date,
            days_back=args.days_back,
        )
        return

    # Start scheduled task
    scheduler = PaperScheduler(
        daily_task_func=daily_task,
        trigger_time=config.trigger_time,
    )
    scheduler.start(run_immediately=True)


if __name__ == "__main__":
    main()
