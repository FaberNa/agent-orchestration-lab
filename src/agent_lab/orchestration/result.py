from dataclasses import dataclass


@dataclass
class OrchestrationResult:
    task: str
    proposal: str
    review: str