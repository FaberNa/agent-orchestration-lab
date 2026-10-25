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

    ):

        self.developer = developer

        self.reviewer = reviewer

    async def run(self, task: str) -> OrchestrationResult:

        context = AgentContext(task=task)
        proposal = await self.developer.run(context)

        reviewer_context = AgentContext(
            task=task,
            previous_output=proposal,
        )
        review = await self.reviewer.run(reviewer_context)

        return OrchestrationResult(
            task=task,
            proposal=proposal,
            review=review,
        )