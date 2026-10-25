from dataclasses import dataclass

from agent_lab.agents.review import ReviewResult


@dataclass
class OrchestrationResult:
    task: str
    proposal: str
    review: ReviewResult