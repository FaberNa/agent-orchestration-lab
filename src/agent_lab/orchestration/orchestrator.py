from agent_lab.agents.developer import DeveloperAgent

from agent_lab.agents.reviewer import ReviewerAgent
from agent_lab.agents.context import AgentContext
from agent_lab.orchestration.result import OrchestrationResult

class AgentOrchestrator:

    """Coordinates the execution of multiple agents."""

    def __init__(

        self,

        developer: DeveloperAgent,

        reviewer: ReviewerAgent,

        max_attempts: int = 3,

    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self.developer = developer

        self.reviewer = reviewer

        self.max_attempts = max_attempts

    async def run(self, task: str) -> OrchestrationResult:
        context = AgentContext(task=task)

        for attempt in range(1, self.max_attempts + 1):
            proposal = await self.developer.run(context)

            reviewer_context = AgentContext(
                task=task,
                previous_output=proposal,
            )
            review = await self.reviewer.run(reviewer_context)

            if review.approved or attempt == self.max_attempts:
                return OrchestrationResult(
                    task=task,
                    proposal=proposal,
                    review=review,
                )

            context = AgentContext(
                task=task,
                previous_output=proposal,
                feedback=review.feedback,
            )

        raise RuntimeError("No orchestration result produced")