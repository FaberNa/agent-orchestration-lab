from agent_lab.agents.base import Agent


class DeveloperAgent(Agent):
    """Agent responsible for proposing implementation solutions."""

    async def run(self, task: str) -> str:
        prompt = (
            "You are a software developer agent.\n"
            "Analyze the following task and propose an implementation:\n\n"
            f"{task}"
        )

        return await self.model.generate(prompt)