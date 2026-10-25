from dataclasses import dataclass

from src.agent_lab.agents.review import ReviewResult


@dataclass
class OrchestrationResult:
    task: str
    proposal: str
    review: ReviewResult