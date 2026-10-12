from agent_lab.agents.base import Agent
from agent_lab.agents.agent_context import AgentContext

class ReviewerAgent(Agent):
    """Agent responsible for reviewing implementation proposals."""

    async def run(self, context: AgentContext) -> str:
        prompt = (
            "You are a software reviewer agent.\n"
            "Review the proposed implementation for the following task.\n\n"
            f"Task:\n{context.task}\n\n"
            f"Proposed implementation:\n{context.previous_output}"
        )

        return await self.model.generate(prompt)
