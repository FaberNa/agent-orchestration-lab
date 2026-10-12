from agent_lab.agents.developer import DeveloperAgent

from agent_lab.agents.reviewer import ReviewerAgent

class AgentOrchestrator:

    """Coordinates the execution of multiple agents."""

    def __init__(

        self,

        developer: DeveloperAgent,

        reviewer: ReviewerAgent,

    ):

        self.developer = developer

        self.reviewer = reviewer

    async def run(self, task: str) -> str:

        proposal = await self.developer.run(task)

        review = await self.reviewer.review(

            task=task,

            proposal=proposal,

        )

        return review