"""
Paper Filter Module
Keyword pre-filter + LLM refinement
"""

import re
from typing import Any, Dict, List, Optional

from openai import OpenAI


class KeywordFilter:
    """Simple keyword-based pre-filter"""

    def __init__(
        self,
        keywords: List[str],
        exclude_keywords: Optional[List[str]] = None,
    ):
        """
        Initialize filter

        Args:
            keywords: Research keywords to match
            exclude_keywords: Keywords to exclude
        """
        self.keywords = [k.lower() for k in keywords]
        self.exclude_keywords = [k.lower() for k in (exclude_keywords or [])]

    def filter_batch(
        self,
        papers: List[Dict[str, Any]],
        threshold: int = 3,
        show_progress: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Filter a batch of papers

        Args:
            papers: List of papers
            threshold: Minimum keyword match count
            show_progress: Show progress bar

        Returns:
            Filtered list of papers
        """
        filtered = []
        for paper in papers:
            score = self._score_paper(paper)
            if score >= threshold:
                paper["relevance_score"] = score
                filtered.append(paper)

        return filtered

    def _score_paper(self, paper: Dict[str, Any]) -> int:
        """Score paper based on keyword matching"""
        text = self._get_text(paper).lower()
        score = 0

        for keyword in self.keywords:
            if keyword in text:
                score += 1

        # Penalty for exclude keywords
        for keyword in self.exclude_keywords:
            if keyword in text:
                score = max(0, score - 2)

        return score

    def _get_text(self, paper: Dict[str, Any]) -> str:
        """Get searchable text from paper"""
        parts = [
            paper.get("title", ""),
            paper.get("abstract", ""),
            paper.get("journal", ""),
        ]

        # Add authors and concepts
        concepts = paper.get("concepts", [])
        if isinstance(concepts, list):
            if concepts and isinstance(concepts[0], dict):
                concepts = [c.get("display_name", "") for c in concepts]
            parts.extend(concepts)

        return " ".join(str(p) for p in parts)


class PaperFilter:
    """LLM-based paper filter"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: str = "",
        base_url: str = "",
        filter_prompt: str = "",
    ):
        """
        Initialize LLM filter

        Args:
            provider: LLM provider (openai, anthropic)
            model: Model name
            api_key: API key
            base_url: API base URL
            filter_prompt: System prompt for filtering
        """
        self.provider = provider
        self.model = model
        self.filter_prompt = filter_prompt

        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None

    def filter_batch(
        self,
        papers: List[Dict[str, Any]],
        threshold: int = 3,
        show_progress: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Filter papers using LLM

        Args:
            papers: List of papers
            threshold: Minimum relevance score
            show_progress: Show progress bar

        Returns:
            Filtered list of papers with scores
        """
        if not self.client:
            print("[Filter] No API key configured, skipping LLM filter")
            return papers

        filtered = []
        iterator = papers

        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(iterator, desc="AI Filtering")

        for paper in iterator:
            result = self.filter_single(
                title=paper.get("title", ""),
                abstract=paper.get("abstract", ""),
            )

            score = result.get("score", 0)
            if score >= threshold:
                paper["relevance_score"] = score
                paper["relevance_reason"] = result.get("reason", "")
                filtered.append(paper)

        return filtered

    def filter_single(
        self,
        title: str,
        abstract: str,
    ) -> Dict[str, Any]:
        """
        Score a single paper

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            Dict with 'score' and 'reason'
        """
        if not self.client:
            return {"score": 3, "reason": "No API key"}

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.filter_prompt},
                    {"role": "user", "content": f"标题：{title}\n\n摘要：{abstract[:2000]}"},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            content = response.choices[0].message.content or ""

            # Parse response
            score_match = re.search(r"评分[:：]?\s*(\d+)", content)
            reason_match = re.search(r"理由[:：]?\s*(.+)", content)

            score = int(score_match.group(1)) if score_match else 3
            reason = reason_match.group(1).strip() if reason_match else content

            return {"score": score, "reason": reason}

        except Exception as e:
            print(f"[Filter] Error: {e}")
            return {"score": 3, "reason": f"Error: {e}"}
