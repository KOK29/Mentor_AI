from __future__ import annotations
from typing import Any
from ...ai.provider import AIProvider


class ResearchEngine:
    def __init__(self, ai: AIProvider) -> None:
        self.ai = ai

    def _normalize_level(self, level: str | None) -> str:
        value = (level or "beginner").lower().strip()
        if value in {"beginner", "intermediate", "advanced"}:
            return value
        return "beginner"

    def _subject_tracks(self, query: str, level: str) -> list[dict[str, str]]:
        lowered = query.lower()
        level_label = self._normalize_level(level)

        if "programming" in lowered or "python" in lowered:
            tracks = {
                "beginner": [
                    ("Python Basics", "https://docs.python.org/3/tutorial/introduction.html"),
                    ("Learn Python by Codecademy", "https://www.codecademy.com/learn/learn-python"),
                    ("Python for Everybody", "https://www.py4e.com/"),
                ],
                "intermediate": [
                    ("Python Data Structures", "https://docs.python.org/3/tutorial/datastructures.html"),
                    ("Python Functions and Modules", "https://docs.python.org/3/tutorial/modules.html"),
                    ("Real Python Tutorials", "https://realpython.com/"),
                ],
                "advanced": [
                    ("Python Async Programming", "https://docs.python.org/3/library/asyncio.html"),
                    ("Design Patterns in Python", "https://refactoring.guru/design-patterns/python"),
                    ("Python Performance Guide", "https://docs.python.org/3/library/timeit.html"),
                ],
            }
            return [{"title": title, "url": url, "publisher": "Official / trusted practice source", "date": "2025", "relevance": "High", "summary": f"A {level_label}-level programming resource for {query}."} for title, url in tracks.get(level_label, tracks["beginner"])]

        if "business" in lowered:
            tracks = {
                "beginner": [
                    ("SBA Business Planning", "https://www.sba.gov/business-guide/plan-your-business"),
                    ("Business Basics", "https://www.investopedia.com/terms/b/business.asp"),
                    ("What is Business Strategy", "https://www.coursera.org/articles/business-strategy"),
                ],
                "intermediate": [
                    ("Strategy Basics", "https://hbr.org/topic/subject/strategy"),
                    ("Marketing Strategy Overview", "https://www.investopedia.com/terms/m/marketing-strategy.asp"),
                    ("Operations Management", "https://www.investopedia.com/terms/o/operations-management.asp"),
                ],
                "advanced": [
                    ("HBR Strategy Articles", "https://hbr.org/topic/subject/strategy"),
                    ("Corporate Finance Institute", "https://corporatefinanceinstitute.com/resources/knowledge/strategy/"),
                    ("MBA Course Strategy Insights", "https://www.coursera.org/learn/strategic-management"),
                ],
            }
            return [{"title": title, "url": url, "publisher": "Business education source", "date": "2025", "relevance": "High", "summary": f"A {level_label}-level business resource on {query}."} for title, url in tracks.get(level_label, tracks["beginner"])]

        if "it" in lowered:
            tracks = {
                "beginner": [
                    ("Google IT Support Certificate", "https://grow.google/it-support/"),
                    ("Microsoft Learn IT Fundamentals", "https://learn.microsoft.com/en-us/training/paths/get-started-with-it-fundamentals/"),
                    ("CompTIA IT Fundamentals", "https://www.comptia.org/certifications/it-fundamentals"),
                ],
                "intermediate": [
                    ("Cisco Networking Basics", "https://www.cisco.com/c/en/us/training-events/training-certifications.html"),
                    ("Microsoft Learn Networking", "https://learn.microsoft.com/en-us/training/paths/networking-fundamentals/"),
                    ("CompTIA Network+", "https://www.comptia.org/certifications/network"),
                ],
                "advanced": [
                    ("Cisco Security Resources", "https://www.cisco.com/c/en/us/training-events/security.html"),
                    ("Microsoft Security Learn", "https://learn.microsoft.com/en-us/training/browse/?products=security"),
                    ("NIST Cybersecurity Guide", "https://www.nist.gov/itl/applied-cybersecurity"),
                ],
            }
            return [{"title": title, "url": url, "publisher": "IT learning source", "date": "2025", "relevance": "High", "summary": f"A {level_label}-level IT source for {query}."} for title, url in tracks.get(level_label, tracks["beginner"])]

        if "computer science" in lowered or "algorithm" in lowered or "systems" in lowered or "theory" in lowered:
            tracks = {
                "beginner": [
                    ("CS50 Intro to CS", "https://cs50.harvard.edu/x/2024/"),
                    ("Khan Academy Computer Science", "https://www.khanacademy.org/computing/computer-science"),
                    ("Understanding Algorithms", "https://www.geeksforgeeks.org/fundamentals-of-algorithms/"),
                ],
                "intermediate": [
                    ("MIT OpenCourseWare CS", "https://ocw.mit.edu/search/?t=Computer%20Science"),
                    ("Data Structures Guide", "https://www.geeksforgeeks.org/data-structures/"),
                    ("Algorithm Design and Analysis", "https://www.coursera.org/specializations/data-structures-algorithms"),
                ],
                "advanced": [
                    ("MIT Distributed Systems", "https://www.mit.edu/~prashask/6.824/"),
                    ("Algorithms, Part II", "https://www.coursera.org/learn/algorithms-part2"),
                    ("Theory of Computation", "https://plato.stanford.edu/entries/computational-complexity/"),
                ],
            }
            return [{"title": title, "url": url, "publisher": "Computer science learning source", "date": "2025", "relevance": "High", "summary": f"A {level_label}-level computer science resource for {query}."} for title, url in tracks.get(level_label, tracks["beginner"])]

        return [
            {
                "title": f"Official learning guide for {query}",
                "url": "https://www.google.com/search?q=" + query.replace(" ", "+"),
                "publisher": "Search-driven reference",
                "date": "2025",
                "relevance": "Medium",
                "summary": f"A practical {level_label}-level source set for {query}.",
            }
        ]

    async def search(self, query: str, limit: int = 5, level: str | None = None) -> dict[str, Any]:
        level_label = self._normalize_level(level)
        prompt = (
            f"Search for reputable sources about: {query}. Return metadata: title, url, publisher, date, relevance, summary. "
            f"Prioritize current, practical, and easy-to-verify references. Focus on a {level_label}-level track. Limit {limit}."
        )
        resp = await self.ai.generate(prompt, model="research-mock")
        payload = resp["output"]["content"] if "output" in resp and isinstance(resp["output"], dict) else {}
        candidate_sources = self._subject_tracks(query, level_label)
        if not candidate_sources:
            candidate_sources = payload.get("sources", [])

        normalized = []
        for index, item in enumerate(candidate_sources[:max(1, int(limit))], start=1):
            item = dict(item)
            item.setdefault("title", f"Resource {index} for {query}")
            item.setdefault("url", "https://www.google.com/search?q=" + query.replace(" ", "+"))
            item.setdefault("publisher", "Verified learning source")
            item.setdefault("relevance", "High" if index <= 2 else "Medium")
            item.setdefault("summary", f"A practical {level_label}-level reference for learning {query} with clear examples.")
            normalized.append(item)

        payload["sources"] = normalized
        payload["level"] = level_label
        payload["query"] = query
        resp["output"] = {**resp.get("output", {}), "content": payload}
        return resp
