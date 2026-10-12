from agent_lab.agents.base import Agent
from agent_lab.agents.context import AgentContext

class DeveloperAgent(Agent):
    """Agent responsible for proposing implementation solutions."""

    async def run(self, context: AgentContext) -> str:
        prompt = (
            "You are a software developer agent.\n"
            "Analyze the following task and propose an implementation:\n\n"
            f"{context.task}"
        )

        return await self.model.generate(prompt)