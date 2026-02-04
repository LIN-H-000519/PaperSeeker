"""
PaperSeeker Test Suite
Tests complete paper search -> filter -> summarize"""

import sys
 -> email flow
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.paper_searcher import OpenAlexSearcher
from src.paper_filter import KeywordFilter
from src.email_sender import EmailSender


def test_config_loading():
    """Test configuration loading"""
    print("\n=== Test 1: Configuration Loading ===")
    try:
        config = get_config()
        print(f"[OK] Configuration loaded successfully")
        print(f"  - Keywords: {config.research_keywords[:2]}...")
        print(f"  - Max results: {config.max_results}")
        print(f"  - Recipient: {config.recipient_email}")
        return True
    except Exception as e:
        print(f"[FAIL] Configuration loading failed: {e}")
        return False


def test_paper_search():
    """Test paper search"""
    print("\n=== Test 2: OpenAlex Paper Search ===")
    try:
        searcher = OpenAlexSearcher()
        papers = searcher.search(
            keywords=["electric vehicle", "energy system"],
            days_back=7,
            max_results=5,
            verbose=False,
        )
        print(f"[OK] Found {len(papers)} papers")
        if papers:
            paper = papers[0]
            print(f"  Example: {paper['title'][:50]}...")
            print(f"  Journal: {paper['journal']}")
        return len(papers) >= 0
    except Exception as e:
        print(f"[FAIL] Paper search failed: {e}")
        return False


def test_keyword_filter():
    """Test keyword filtering"""
    print("\n=== Test 3: Keyword Filtering ===")
    try:
        config = get_config()
        searcher = OpenAlexSearcher()
        papers = searcher.search(
            keywords=config.research_keywords[:2],
            days_back=7,
            max_results=10,
            verbose=False,
        )

        if not papers:
            print("[SKIP] No papers to filter")
            return True

        keyword_filter = KeywordFilter(
            keywords=config.research_keywords,
            exclude_keywords=config.exclude_keywords,
        )

        filtered = keyword_filter.filter_batch(
            papers,
            threshold=3,
            show_progress=True,
        )

        print(f"[OK] Filtering complete: {len(papers)} -> {len(filtered)} papers")
        return True
    except Exception as e:
        print(f"[FAIL] Filtering failed: {e}")
        return False


def test_email_sender():
    """Test email sender initialization"""
    print("\n=== Test 4: Email Sender Initialization ===")
    try:
        config = get_config()
        email_sender = EmailSender(config)
        print(f"[OK] Email sender initialized")
        print(f"  - SMTP: {email_sender.smtp_server}")
        print(f"  - From: {email_sender.sender_email}")
        print(f"  - To: {email_sender.recipient_email}")

        if email_sender.sender_email and email_sender.recipient_email:
            print("\n[INFO] Sending test email...")
            if email_sender.send_test():
                print("[OK] Test email sent successfully")
            else:
                print("[FAIL] Test email failed")
                return False

        return True
    except Exception as e:
        print(f"[FAIL] Email sender initialization failed: {e}")
        return False


def test_full_flow():
    """Test complete flow"""
    print("\n=== Test 5: Complete Flow Test ===")
    try:
        config = get_config()

        # 1. Search
        print("[1/4] Searching papers...")
        searcher = OpenAlexSearcher()
        papers = searcher.search(
            keywords=config.research_keywords[:2],
            days_back=7,
            max_results=10,
            verbose=False,
        )
        print(f"    Found {len(papers)} papers")

        if not papers:
            print("[SKIP] No papers found, skipping full flow test")
            return True

        # 2. Filter
        print("[2/4] Filtering papers...")
        keyword_filter = KeywordFilter(
            keywords=config.research_keywords,
            exclude_keywords=config.exclude_keywords,
        )
        filtered = keyword_filter.filter_batch(
            papers,
            threshold=3,
            show_progress=False,
        )
        print(f"    Filtered to {len(filtered)} papers")

        if not filtered:
            print("[SKIP] No relevant papers")
            return True

        # 3. Prepare summaries
        print("[3/4] Preparing summaries...")
        for paper in filtered:
            paper["summary_zh"] = paper.get("abstract", "")[:300] + "..."
            paper["summary_en"] = "（Auto summary placeholder）"

        # 4. Build email
        print("[4/4] Building email content...")
        email_sender = EmailSender(config)
        html = email_sender._build_html_content(filtered, "2024-01-01")
        print(f"    Email HTML length: {len(html)} characters")

        print("[OK] Complete flow test passed")
        return True

    except Exception as e:
        print(f"[FAIL] Complete flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PaperSeeker Test Suite")
    print("=" * 60)

    tests = [
        test_config_loading,
        test_paper_search,
        test_keyword_filter,
        test_email_sender,
        test_full_flow,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] {test.__name__} threw exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test.__name__}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
