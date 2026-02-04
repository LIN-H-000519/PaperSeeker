"""
Abstract Summarizer Module
Generates bilingual summaries using LLM
"""

from typing import Any, Dict, List

from openai import OpenAI


class AbstractSummarizer:
    """Generate bilingual paper summaries"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: str = "",
        base_url: str = "",
        summarize_prompt: str = "",
    ):
        """
        Initialize summarizer

        Args:
            provider: LLM provider
            model: Model name
            api_key: API key
            base_url: API base URL
            summarize_prompt: Prompt template
        """
        self.provider = provider
        self.model = model
        self.summarize_prompt = summarize_prompt

        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None

    def summarize_batch(
        self,
        papers: List[Dict[str, Any]],
        show_progress: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Generate summaries for papers

        Args:
            papers: List of papers
            show_progress: Show progress bar

        Returns:
            Papers with summaries added
        """
        if not self.client:
            print("[Summarizer] No API key configured, skipping summarization")
            return papers

        results = []
        iterator = papers

        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(iterator, desc="Generating Summaries")

        for paper in iterator:
            summary = self._summarize_paper(paper)
            paper["summary_zh"] = summary.get("zh", "")
            paper["summary_en"] = summary.get("en", paper.get("abstract", ""))
            results.append(paper)

        return results

    def _summarize_paper(self, paper: Dict[str, Any]) -> Dict[str, str]:
        """
        Summarize a single paper

        Args:
            paper: Paper dictionary

        Returns:
            Dict with 'zh' and 'en' summaries
        """
        title = paper.get("title", "")
        authors = paper.get("authors", "")
        journal = paper.get("journal", "")
        abstract = paper.get("abstract", "")

        if not abstract:
            return {
                "zh": "（原文摘要不可用）",
 "(Abstract                "en": not available)",
            }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.summarize_prompt},
                    {"role": "user", "content": f"标题：{title}\n作者：{authors}\n期刊：{journal}\n原文摘要：{abstract}"},
                ],
                temperature=0.5,
                max_tokens=500,
            )

            content = response.choices[0].message.content or ""

            # Parse bilingual summary
            zh_match = content.find("【中文摘要】")
            en_match = content.find("English Abstract:")

            zh = ""
            if zh_match != -1 and en_match != -1:
                zh = content[zh_match + 6:en_match].strip()
            elif zh_match != -1:
                zh = content[zh_match + 6:].strip()

            en = ""
            if en_match != -1:
                en = content[en_match + 17:].strip()

            return {"zh": zh, "en": en}

        except Exception as e:
            print(f"[Summarizer] Error: {e}")
            return {
                "zh": f"（摘要生成失败）",
                "en": f"(Summary generation failed: {e})",
            }
