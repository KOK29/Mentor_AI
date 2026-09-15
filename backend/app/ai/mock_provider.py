from __future__ import annotations
import re
from .provider import AIProvider
from typing import Any


class MockAIProvider(AIProvider):
    @staticmethod
    def _official_source_map(topic: str) -> list[dict[str, str]]:
        lowered = topic.lower()
        if any(keyword in lowered for keyword in ["programming", "python", "software", "code", "development"]):
            return [
                {
                    "title": "Python Official Documentation",
                    "url": "https://docs.python.org/3/",
                    "publisher": "Python Software Foundation",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "Official Python reference for syntax, modules, and practical language learning.",
                },
                {
                    "title": "MDN Web Docs",
                    "url": "https://developer.mozilla.org/",
                    "publisher": "Mozilla",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "Official web platform documentation for programming concepts and browser-based development.",
                },
                {
                    "title": "Microsoft Learn for Developers",
                    "url": "https://learn.microsoft.com/en-us/",
                    "publisher": "Microsoft",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "Official Microsoft learning platform covering programming, software engineering, and modern app development.",
                },
            ]
        if any(keyword in lowered for keyword in ["business", "strategy", "marketing", "management", "finance"]):
            return [
                {
                    "title": "SBA Business Planning Guide",
                    "url": "https://www.sba.gov/business-guide/plan-your-business",
                    "publisher": "U.S. Small Business Administration",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "Official business planning guide covering strategy, operations, and practical decision-making.",
                },
                {
                    "title": "Harvard Business Review",
                    "url": "https://hbr.org/",
                    "publisher": "Harvard Business Review",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "A respected source for strategy, leadership, and modern business thinking.",
                },
                {
                    "title": "World Bank Open Learning Campus",
                    "url": "https://olc.worldbank.org/",
                    "publisher": "World Bank",
                    "date": "2025",
                    "relevance": "Medium",
                    "summary": "Official development and business education resources for market, finance, and strategy topics.",
                },
            ]
        if any(keyword in lowered for keyword in ["it", "support", "network", "system", "cyber", "security", "infrastructure"]):
            return [
                {
                    "title": "Microsoft Learn: IT and Infrastructure",
                    "url": "https://learn.microsoft.com/en-us/training/browse/?products=windows&resource_type=learning%20path",
                    "publisher": "Microsoft",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "Official learning paths for IT, systems, and support operations.",
                },
                {
                    "title": "Cisco Learning and Certifications",
                    "url": "https://www.cisco.com/c/en/us/training-events.html",
                    "publisher": "Cisco",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "Official Cisco resources covering networking, systems, and digital infrastructure fundamentals.",
                },
                {
                    "title": "Google IT Support Professional Certificate",
                    "url": "https://grow.google/it-support/",
                    "publisher": "Google",
                    "date": "2025",
                    "relevance": "Medium",
                    "summary": "Structured official digital learning content for IT support and troubleshooting skills.",
                },
            ]
        if any(keyword in lowered for keyword in ["computer science", "algorithm", "data structure", "architecture", "systems", "ai", "database"]):
            return [
                {
                    "title": "CS50 Introduction to Computer Science",
                    "url": "https://cs50.harvard.edu/x/2024/",
                    "publisher": "Harvard University",
                    "date": "2024",
                    "relevance": "High",
                    "summary": "Official Harvard CS curriculum covering foundations, algorithms, and practical problem solving.",
                },
                {
                    "title": "MIT OpenCourseWare - Algorithms and Systems",
                    "url": "https://ocw.mit.edu/search/?t=Computer%20Science",
                    "publisher": "MIT",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "Official MIT educational resources on algorithms, systems, and computer science theory.",
                },
                {
                    "title": "Theory of Computation Overview",
                    "url": "https://plato.stanford.edu/entries/computational-complexity/",
                    "publisher": "Stanford Encyclopedia of Philosophy",
                    "date": "2025",
                    "relevance": "High",
                    "summary": "A strong theoretical reference for complexity, proof-based reasoning, and computational theory.",
                },
            ]
        return [
            {
                "title": "Official learning resources",
                "url": "https://www.official-docs.example.org/",
                "publisher": "Educational resources",
                "date": "2025",
                "relevance": "Medium",
                "summary": "A general reference page for structured learning and research.",
            }
        ]

    async def generate(self, prompt: str, *, model: str | None = None) -> Any:
        lower_prompt = prompt.lower()

        if lower_prompt.startswith("teach ") or "structure: concept" in lower_prompt:
            topic_match = re.search(r"teach\s+(.+?)\s+at\s+([a-z]+)\s+level", prompt, re.IGNORECASE)
            topic = topic_match.group(1).strip() if topic_match else "the selected subject"
            level = topic_match.group(2).strip() if topic_match else "beginner"
            return {
                "prompt": prompt,
                "model": model or "teaching-mock",
                "output": {
                    "type": "teaching",
                    "content": {
                        "topic": topic,
                        "level": level,
                        "concept": f"The core idea behind {topic} is to understand the essential principles, patterns, and practical applications that make it useful.",
                        "simple_explanation": f"At the {level} level, {topic} can be understood as a practical foundation you build on step by step with examples, repetition, and guided exercises.",
                        "detailed_explanation": f"To learn {topic} well, start with the basic concepts, connect them to real use cases, then move into analysis, application, and problem solving. This creates a strong progression from beginner understanding to advanced mastery.",
                        "example": f"Example: a beginner might explain the basic definition, while an advanced learner can compare trade-offs, solve complex problems, and optimize strategies in {topic}.",
                        "practice_question": f"Why is understanding the foundation of {topic} important before moving to more advanced problems?",
                        "next_steps": [
                            "Review the basic definitions",
                            "Practice with guided examples",
                            "Apply the concept to a realistic task",
                            "Solve advanced challenges with justification",
                        ],
                    },
                },
            }

        if "analyze the mistake" in lower_prompt or "student:" in lower_prompt and "correct:" in lower_prompt:
            student_match = re.search(r"student:\s*(.+?)\s*\.\s*correct:", prompt, re.IGNORECASE)
            correct_match = re.search(r"correct:\s*(.+?)(?:\.|$)", prompt, re.IGNORECASE)
            context_match = re.search(r"context:\s*(.*)$", prompt, re.IGNORECASE)
            student_answer = student_match.group(1).strip() if student_match else "the student's answer"
            correct_answer = correct_match.group(1).strip() if correct_match else "the correct answer"
            context = context_match.group(1).strip() if context_match else "the current topic"
            return {
                "prompt": prompt,
                "model": model or "mistake-analysis-mock",
                "output": {
                    "type": "mistake_analysis",
                    "content": {
                        "summary": f"The answer '{student_answer}' missed the key principle behind {context}.",
                        "root_cause": f"The main issue is that the reasoning was not aligned with the correct fact: '{correct_answer}'. Review the concept and compare it to the expected outcome.",
                        "improvement_steps": [
                            "Re-read the core definition before choosing an answer.",
                            "Compare your reasoning against the correct principle.",
                            "Practice a similar problem to strengthen recall.",
                            "Check whether the answer matches the exact requirement of the question.",
                        ],
                    },
                },
            }

        if "exercise" in lower_prompt or "generate a" in lower_prompt or "mcq" in lower_prompt:
            topic_match = re.search(r"topic:\s*(.+?)(?:\.|$)", prompt, re.IGNORECASE)
            topic = topic_match.group(1).strip() if topic_match else "the subject"
            level_match = re.search(r"generate a\s+([a-z]+)\s+.*exercise", prompt, re.IGNORECASE)
            difficulty = level_match.group(1).strip() if level_match else "medium"
            return {
                "prompt": prompt,
                "model": model or "practice-mock",
                "output": {
                    "type": "practice",
                    "content": {
                        "topic": topic,
                        "level": difficulty,
                        "question": f"Which answer best demonstrates a strong understanding of {topic} at the {difficulty} level?",
                        "choices": [
                            f"It is the basic foundation needed to understand {topic}.",
                            f"It is only useful for advanced specialists in {topic}.",
                            f"It is unrelated to practical understanding of {topic}.",
                            f"It is a memorized fact that should not be applied in {topic}.",
                        ],
                        "correct_answer": f"It is the basic foundation needed to understand {topic}.",
                        "explanation": f"A solid understanding of {topic} begins with the fundamentals, then grows through applied examples and deeper analysis.",
                    },
                },
            }

        if "search for" in lower_prompt or "sources" in lower_prompt or "reputable" in lower_prompt:
            topic_match = re.search(r"about:\s*(.+?)(?:\. Return|$)", prompt, re.IGNORECASE)
            topic = topic_match.group(1).strip() if topic_match else "the selected subject"
            sources = self._official_source_map(topic)
            return {
                "prompt": prompt,
                "model": model or "research-mock",
                "output": {
                    "type": "research",
                    "content": {
                        "topic": topic,
                        "sources": sources,
                        "query": topic,
                    },
                },
            }

        return {
            "prompt": prompt,
            "model": model or "teaching-mock",
            "output": {
                "type": "teaching",
                "content": {
                    "topic": "the selected subject",
                    "level": "beginner",
                    "concept": "Build a strong foundation first, then connect the idea to real practice and advanced problem solving.",
                    "simple_explanation": "This subject becomes easier when you understand the core idea before moving into detail.",
                    "detailed_explanation": "The strongest learning path is: understand the core idea, practice the basic examples, test your understanding, and then solve more complex challenges.",
                    "example": "A skill grows from basic understanding to confident application and expert reasoning.",
                    "practice_question": "What is the next step after understanding the core idea of the topic?",
                    "next_steps": ["Learn the fundamentals", "Apply to real examples", "Review mistakes", "Tackle advanced problems"],
                },
            },
        }
