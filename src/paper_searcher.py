"""
OpenAlex Paper Search Module
Searches academic papers from OpenAlex API
"""

import time
from typing import Any, Dict, List, Optional

import requests
from tqdm import tqdm


class OpenAlexSearcher:
    """OpenAlex API paper search"""

    def __init__(self, api_url: str = "https://api.openalex.org"):
        """
        Initialize searcher

        Args:
            api_url: OpenAlex API base URL
        """
        self.api_url = api_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PaperSeeker/1.0",
            "Accept": "application/json",
        })

    def search(
        self,
        keywords: List[str],
        exclude_keywords: Optional[List[str]] = None,
        days_back: int = 7,
        max_results: int = 20,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        verbose: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search papers by keywords

        Args:
            keywords: List of research keywords
            exclude_keywords: Keywords to exclude
            days_back: Search recent N days (used if from_date not specified)
            max_results: Maximum results per keyword
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            verbose: Verbose output

        Returns:
            List of paper dictionaries
        """
        # Calculate date filter
        if from_date:
            from_dt = from_date
        else:
            from_dt = self._days_ago(days_back)

        if to_date:
            to_dt = to_date
        else:
            from_dt = self._days_ago(days_back)  # Refresh from_dt

        all_papers = []
        seen_ids = set()

        if verbose:
            print(f"[Searcher] Searching from {from_dt} to {to_dt}...")

        for keyword in keywords:
            papers = self._search_single_keyword(
                keyword,
                from_date=from_dt,
                to_date=to_dt,
                max_results=max_results,
            )

            # Remove duplicates
            new_papers = []
            for paper in papers:
                paper_id = paper.get("id", "")
                if paper_id and paper_id not in seen_ids:
                    seen_ids.add(paper_id)
                    new_papers.append(paper)

            all_papers.extend(new_papers)

            if verbose:
                print(f"  Keyword '{keyword}': found {len(papers)} papers ({len(new_papers)} new)")

            # Rate limiting
            time.sleep(0.5)

        # Sort by publication date (newest first)
        all_papers.sort(key=lambda x: x.get("publication_date", ""), reverse=True)

        if verbose:
            print(f"[Searcher] Total: {len(all_papers)} unique papers")

        return all_papers

    def _search_single_keyword(
        self,
        keyword: str,
        from_date: str,
        to_date: str,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Search papers for a single keyword

        Args:
            keyword: Search keyword
            from_date: Start date
            to_date: End date
            max_results: Maximum results

        Returns:
            List of paper dictionaries
        """
        # Build query
        query = f"""
            {{
                works(
                    search: "{keyword}",
                    filter: "from_publication_date:{from_date},to_publication_date:{to_date}",
                    sort: "publication_date:desc",
                    per_page: {min(max_results, 100)}
                ) {{
                    results {{
                        id
                        doi
                        title
                        publication_date
                        publication_year
                        journal {{
                            id
                            display_name
                        }}
                        authorships {{
                            author {{
                                id
                                display_name
                            }}
                        }}
                        abstract
                        language
                        keywords {{
                            id
                            display_name
                        }}
                        concepts {{
                            id
                            display_name
                            level
                        }}
                    }}
                }}
            }}
        """

        url = f"{self.api_url}/graphql"
        headers = {"Content-Type": "application/json"}

        try:
            response = self.session.post(url, json={"query": query.strip()}, timeout=30)
            response.raise_for_status()
            data = response.json()

            works = data.get("data", {}).get("works", {}).get("results", [])

            # Handle GraphQL structure
            if not works and "errors" in data:
                # Fallback: try REST API
                return self._search_rest_api(keyword, from_date, to_date, max_results)

            return [self._parse_work(work) for work in works]

        except requests.exceptions.RequestException as e:
            print(f"[Searcher] Error searching '{keyword}': {e}")
            return self._search_rest_api(keyword, from_date, to_date, max_results)

    def _search_rest_api(
        self,
        keyword: str,
        from_date: str,
        to_date: str,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Fallback: Search using REST API

        Args:
            keyword: Search keyword
            from_date: Start date
            to_date: End date
            max_results: Maximum results

        Returns:
            List of paper dictionaries
        """
        url = f"{self.api_url}/works"
        params = {
            "search": keyword,
            "filter": f"from_publication_date:{from_date},to_publication_date:{to_date}",
            "sort": "publication_date:desc",
            "per-page": min(max_results, 100),
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            return [self._parse_work(work) for work in results]

        except requests.exceptions.RequestException as e:
            print(f"[Searcher] REST API error for '{keyword}': {e}")
            return []

    def _parse_work(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAlex work to simplified format"""
        # Extract authors
        authors = []
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            if author:
                authors.append(author.get("display_name", ""))

        # Extract journal/conference
        host = work.get("journal", {})
        journal = host.get("display_name", "") if host else ""

        # Extract concepts/topics
        concepts = []
        for concept in work.get("concepts", []):
            if concept.get("level", 0) == 0:  # Top-level concepts
                concepts.append(concept.get("display_name", ""))

        # Extract keywords
        keywords = []
        for kw in work.get("keywords", []):
            keywords.append(kw.get("display_name", ""))

        return {
            "id": work.get("id", "").split("/")[-1] if work.get("id") else "",
            "doi": work.get("doi", ""),
            "title": work.get("title", ""),
            "publication_date": work.get("publication_date", ""),
            "journal": journal,
            "authors": ", ".join(authors[:5]),  # Limit to 5 authors
            "abstract": work.get("abstract", ""),
            "language": work.get("language", "en"),
            "concepts": concepts,
            "keywords": keywords,
            "openalex_url": work.get("id", ""),
        }

    def _days_ago(self, days: int) -> str:
        """Get date string for N days ago"""
        from datetime import datetime, timedelta
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")
