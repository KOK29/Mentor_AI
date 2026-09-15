from __future__ import annotations
from typing import Any, Optional
from ...ai.provider import AIProvider


class TeachingEngine:
    """Subject-aware teaching engine with level-based progression metadata."""

    def __init__(self, ai: AIProvider, feedback_repo: Optional[Any] = None) -> None:
        self.ai = ai
        self._feedback = feedback_repo

    def _normalize_level(self, level: str) -> str:
        value = (level or "beginner").lower().strip()
        return value if value in {"beginner", "intermediate", "advanced"} else "beginner"

    def _get_domain_profile(self, topic: str) -> dict[str, Any]:
        lowered = topic.lower()
        if any(token in lowered for token in ["business", "marketing", "finance", "management", "strategy", "economics"]):
            return {
                "domain": "Business",
                "curriculum_tree": [
                    {"stage": "Foundation", "title": "Business foundations", "goal": "Understand value creation, customers, and core business decisions."},
                    {"stage": "Strategy", "title": "Market and strategy", "goal": "Analyze positioning, competition, and long-term direction."},
                    {"stage": "Operations", "title": "Operations and execution", "goal": "Turn strategy into plans, metrics, and measurable execution."},
                    {"stage": "Leadership", "title": "Decision-making and growth", "goal": "Prioritize trade-offs, manage risk, and scale outcomes."},
                ],
                "real_world_applications": [
                    "Designing a product launch strategy for a new market",
                    "Analyzing cost, revenue, and customer value for a business decision",
                    "Improving an operational process with measurable KPIs",
                ],
            }
        if any(token in lowered for token in ["it", "support", "system", "network", "cyber", "security", "infrastructure", "operations"]):
            return {
                "domain": "IT",
                "curriculum_tree": [
                    {"stage": "Foundation", "title": "IT essentials", "goal": "Understand devices, workflows, and system basics."},
                    {"stage": "Operations", "title": "Network and troubleshooting", "goal": "Diagnose issues and support stable digital services."},
                    {"stage": "Security", "title": "Access and protection", "goal": "Apply safe practices and maintain secure configurations."},
                    {"stage": "Support", "title": "Service and recovery", "goal": "Resolve incidents and communicate clearly with users."},
                ],
                "real_world_applications": [
                    "Troubleshooting login, connectivity, or device issues in a workplace",
                    "Supporting a small office with hardware, software, and network setup",
                    "Applying change control and recovery steps during downtime",
                ],
            }
        if any(token in lowered for token in ["programming", "software", "python", "javascript", "java", "code", "development", "algorithms", "data structures"]):
            return {
                "domain": "Programming",
                "curriculum_tree": [
                    {"stage": "Foundation", "title": "Programming basics", "goal": "Learn syntax, logic, and problem decomposition."},
                    {"stage": "Data", "title": "Data structures and logic", "goal": "Work with variables, collections, and flow control."},
                    {"stage": "Design", "title": "Algorithms and patterns", "goal": "Solve problems efficiently and write reusable logic."},
                    {"stage": "Build", "title": "Testing and systems", "goal": "Create reliable software and validate real use cases."},
                ],
                "real_world_applications": [
                    "Building a small automation script for repetitive work",
                    "Creating a web feature using clean logic and validation",
                    "Debugging a workflow and testing code for reliability",
                ],
            }
        if any(token in lowered for token in ["computer science", "cs", "algorithm", "architecture", "database", "networking", "os", "systems", "ai", "data science"]):
            return {
                "domain": "Computer Science",
                "curriculum_tree": [
                    {"stage": "Theory", "title": "Core CS concepts", "goal": "Understand logic, abstraction, and computational thinking."},
                    {"stage": "Structures", "title": "Algorithms and data structures", "goal": "Compare efficiency and choose the right model."},
                    {"stage": "Systems", "title": "Architecture and operating systems", "goal": "Study how software and hardware work together."},
                    {"stage": "Advanced", "title": "Scalable systems and design", "goal": "Reason about performance, trade-offs, and large-scale systems."},
                ],
                "real_world_applications": [
                    "Designing a faster algorithm for an application workflow",
                    "Choosing data structures for performance-critical systems",
                    "Evaluating system trade-offs in architecture and distributed computing",
                ],
            }
        return {
            "domain": "General study",
            "curriculum_tree": [
                {"stage": "Foundation", "title": "Concept basics", "goal": "Learn the essential definition and core idea."},
                {"stage": "Application", "title": "Examples and practice", "goal": "Use the concept in realistic tasks and guided examples."},
                {"stage": "Mastery", "title": "Reasoning and transfer", "goal": "Explain, compare, and apply the idea in new contexts."},
            ],
            "real_world_applications": [
                "Apply the concept in a realistic scenario",
                "Explain the reasoning behind the solution",
                "Transfer the idea to a related challenge",
            ],
        }

    def _build_lesson_payload(self, topic: str, level: str, language: str) -> dict[str, Any]:
        level_name = self._normalize_level(level)
        language_name = (language or "en").upper()
        domain_profile = self._get_domain_profile(topic)
        skill_map = {
            "beginner": ["Core definition", "Simple example", "Worked explanation"],
            "intermediate": ["Concept connection", "Pattern comparison", "Contextual use"],
            "advanced": ["Reasoning trade-offs", "Optimization", "Expert synthesis"],
        }
        objectives = [
            f"Understand the fundamentals of {topic}",
            f"Apply {topic} in a realistic scenario",
            f"Explain the reasoning behind key {topic} decisions",
        ]
        milestones = [
            "Master the basic definition and key terms",
            "Solve a guided example with confidence",
            "Explain why the concept works in context",
            "Transfer the idea to a new task or challenge",
        ]
        return {
            "topic": topic,
            "level": level_name,
            "language": language_name,
            "domain": domain_profile["domain"],
            "title": f"{topic} essentials for {level_name} learners",
            "concept": f"{topic} becomes easier to learn when you connect the core idea to a practical example and then test your understanding with feedback.",
            "simple_explanation": f"At the {level_name} stage, the main goal is to understand the essential pattern in {topic} and use it in short, clear examples.",
            "detailed_explanation": f"A strong learning path for {topic} is: define the concept, study a guided example, compare the reasoning with other cases, then apply the pattern to a realistic task. This helps turn memorization into usable understanding.",
            "example": f"Example: a learner practicing {topic} starts by identifying the core rule, tests it on a familiar scenario, and then checks whether the reasoning still works in a more complex case.",
            "practice_question": f"Why is it important to connect your understanding of {topic} to a real example before moving to harder problems?",
            "learning_objectives": objectives,
            "milestones": milestones,
            "curriculum_tree": domain_profile["curriculum_tree"],
            "real_world_applications": domain_profile["real_world_applications"],
            "next_steps": [
                "Review the definition",
                "Practice a worked example",
                "Apply the idea to a small challenge",
                "Reflect on what changed after feedback",
            ],
            "skill_focus": skill_map[level_name],
            "human_trained": False,  # flag flipped to True when a correction is applied
        }

    async def teach(self, topic: str, level: str = "beginner", language: str = "en") -> dict[str, Any]:
        level_name = self._normalize_level(level)
        prompt = (
            f"Teach {topic} at {level} level in {language}. "
            "Structure: concept, simple_explanation, detailed_explanation, example, practice_question, "
            "learning_objectives, milestones, next_steps, skill_focus."
        )
        resp = await self.ai.generate(prompt, model="teaching-mock")
        payload = resp["output"]["content"] if "output" in resp and isinstance(resp["output"], dict) else {}
        merged = {**self._build_lesson_payload(topic, level, language), **payload}

        # ── Apply human training correction if available ──────────────────
        if self._feedback is not None:
            try:
                correction = await self._feedback.get_best_correction("teaching", topic, level_name)
                if correction:
                    merged = {**merged, **correction, "human_trained": True}
            except Exception:
                pass  # Never let training lookup break the main response
        # ──────────────────────────────────────────────────────────────────

        resp["output"] = {**resp.get("output", {}), "content": merged}
        return resp


    def _normalize_level(self, level: str) -> str:
        value = (level or "beginner").lower().strip()
        return value if value in {"beginner", "intermediate", "advanced"} else "beginner"

    def _get_domain_profile(self, topic: str) -> dict[str, Any]:
        lowered = topic.lower()
        if any(token in lowered for token in ["business", "marketing", "finance", "management", "strategy", "economics"]):
            return {
                "domain": "Business",
                "curriculum_tree": [
                    {"stage": "Foundation", "title": "Business foundations", "goal": "Understand value creation, customers, and core business decisions."},
                    {"stage": "Strategy", "title": "Market and strategy", "goal": "Analyze positioning, competition, and long-term direction."},
                    {"stage": "Operations", "title": "Operations and execution", "goal": "Turn strategy into plans, metrics, and measurable execution."},
                    {"stage": "Leadership", "title": "Decision-making and growth", "goal": "Prioritize trade-offs, manage risk, and scale outcomes."},
                ],
                "real_world_applications": [
                    "Designing a product launch strategy for a new market",
                    "Analyzing cost, revenue, and customer value for a business decision",
                    "Improving an operational process with measurable KPIs",
                ],
            }
        if any(token in lowered for token in ["it", "support", "system", "network", "cyber", "security", "infrastructure", "operations"]):
            return {
                "domain": "IT",
                "curriculum_tree": [
                    {"stage": "Foundation", "title": "IT essentials", "goal": "Understand devices, workflows, and system basics."},
                    {"stage": "Operations", "title": "Network and troubleshooting", "goal": "Diagnose issues and support stable digital services."},
                    {"stage": "Security", "title": "Access and protection", "goal": "Apply safe practices and maintain secure configurations."},
                    {"stage": "Support", "title": "Service and recovery", "goal": "Resolve incidents and communicate clearly with users."},
                ],
                "real_world_applications": [
                    "Troubleshooting login, connectivity, or device issues in a workplace",
                    "Supporting a small office with hardware, software, and network setup",
                    "Applying change control and recovery steps during downtime",
                ],
            }
        if any(token in lowered for token in ["programming", "software", "python", "javascript", "java", "code", "development", "algorithms", "data structures"]):
            return {
                "domain": "Programming",
                "curriculum_tree": [
                    {"stage": "Foundation", "title": "Programming basics", "goal": "Learn syntax, logic, and problem decomposition."},
                    {"stage": "Data", "title": "Data structures and logic", "goal": "Work with variables, collections, and flow control."},
                    {"stage": "Design", "title": "Algorithms and patterns", "goal": "Solve problems efficiently and write reusable logic."},
                    {"stage": "Build", "title": "Testing and systems", "goal": "Create reliable software and validate real use cases."},
                ],
                "real_world_applications": [
                    "Building a small automation script for repetitive work",
                    "Creating a web feature using clean logic and validation",
                    "Debugging a workflow and testing code for reliability",
                ],
            }
        if any(token in lowered for token in ["computer science", "cs", "algorithm", "architecture", "database", "networking", "os", "systems", "ai", "data science"]):
            return {
                "domain": "Computer Science",
                "curriculum_tree": [
                    {"stage": "Theory", "title": "Core CS concepts", "goal": "Understand logic, abstraction, and computational thinking."},
                    {"stage": "Structures", "title": "Algorithms and data structures", "goal": "Compare efficiency and choose the right model."},
                    {"stage": "Systems", "title": "Architecture and operating systems", "goal": "Study how software and hardware work together."},
                    {"stage": "Advanced", "title": "Scalable systems and design", "goal": "Reason about performance, trade-offs, and large-scale systems."},
                ],
                "real_world_applications": [
                    "Designing a faster algorithm for an application workflow",
                    "Choosing data structures for performance-critical systems",
                    "Evaluating system trade-offs in architecture and distributed computing",
                ],
            }
        return {
            "domain": "General study",
            "curriculum_tree": [
                {"stage": "Foundation", "title": "Concept basics", "goal": "Learn the essential definition and core idea."},
                {"stage": "Application", "title": "Examples and practice", "goal": "Use the concept in realistic tasks and guided examples."},
                {"stage": "Mastery", "title": "Reasoning and transfer", "goal": "Explain, compare, and apply the idea in new contexts."},
            ],
            "real_world_applications": [
                "Apply the concept in a realistic scenario",
                "Explain the reasoning behind the solution",
                "Transfer the idea to a related challenge",
            ],
        }

    def _build_lesson_payload(self, topic: str, level: str, language: str) -> dict[str, Any]:
        level_name = self._normalize_level(level)
        language_name = (language or "en").upper()
        domain_profile = self._get_domain_profile(topic)
        skill_map = {
            "beginner": ["Core definition", "Simple example", "Worked explanation"],
            "intermediate": ["Concept connection", "Pattern comparison", "Contextual use"],
            "advanced": ["Reasoning trade-offs", "Optimization", "Expert synthesis"],
        }
        objectives = [
            f"Understand the fundamentals of {topic}",
            f"Apply {topic} in a realistic scenario",
            f"Explain the reasoning behind key {topic} decisions",
        ]
        milestones = [
            "Master the basic definition and key terms",
            "Solve a guided example with confidence",
            "Explain why the concept works in context",
            "Transfer the idea to a new task or challenge",
        ]
        return {
            "topic": topic,
            "level": level_name,
            "language": language_name,
            "domain": domain_profile["domain"],
            "title": f"{topic} essentials for {level_name} learners",
            "concept": f"{topic} becomes easier to learn when you connect the core idea to a practical example and then test your understanding with feedback.",
            "simple_explanation": f"At the {level_name} stage, the main goal is to understand the essential pattern in {topic} and use it in short, clear examples.",
            "detailed_explanation": f"A strong learning path for {topic} is: define the concept, study a guided example, compare the reasoning with other cases, then apply the pattern to a realistic task. This helps turn memorization into usable understanding.",
            "example": f"Example: a learner practicing {topic} starts by identifying the core rule, tests it on a familiar scenario, and then checks whether the reasoning still works in a more complex case.",
            "practice_question": f"Why is it important to connect your understanding of {topic} to a real example before moving to harder problems?",
            "learning_objectives": objectives,
            "milestones": milestones,
            "curriculum_tree": domain_profile["curriculum_tree"],
            "real_world_applications": domain_profile["real_world_applications"],
            "next_steps": [
                "Review the definition",
                "Practice a worked example",
                "Apply the idea to a small challenge",
                "Reflect on what changed after feedback",
            ],
            "skill_focus": skill_map[level_name],
        }

    async def teach(self, topic: str, level: str = "beginner", language: str = "en") -> dict[str, Any]:
        prompt = (
            f"Teach {topic} at {level} level in {language}. "
            "Structure: concept, simple_explanation, detailed_explanation, example, practice_question, "
            "learning_objectives, milestones, next_steps, skill_focus."
        )
        resp = await self.ai.generate(prompt, model="teaching-mock")
        payload = resp["output"]["content"] if "output" in resp and isinstance(resp["output"], dict) else {}
        merged = {**self._build_lesson_payload(topic, level, language), **payload}
        resp["output"] = {**resp.get("output", {}), "content": merged}
        return resp
