from dataclasses import dataclass

@dataclass
class ReviewResult:
    approved: bool
    feedback: str
