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
        if context.previous_output is not None:
            prompt += (
                "\n\nPrevious implementation:\n"
                f"{context.previous_output}"
            )

        if context.feedback is not None:
            prompt += (
                "\n\nReviewer feedback:\n"
                f"{context.feedback}\n\n"
                "Revise the implementation to address the reviewer feedback."
            )

        return await self.model.generate(prompt)