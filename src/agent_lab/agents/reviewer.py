import json

from agent_lab.agents.base import Agent
from agent_lab.agents.context import AgentContext
from agent_lab.agents.review import ReviewResult

class ReviewerAgent(Agent):
    """Agent responsible for reviewing implementation proposals."""


    async def run(self, context: AgentContext) -> ReviewResult:
        prompt = (
            "You are a software reviewer agent.\n"
            "Review the proposed implementation for the following task.\n"
            "Approve only if no required corrections remain.\n"
            "Return only a JSON object with these fields:\n"
            '- "approved": a boolean\n'
            '- "feedback": a string explaining your decision '
            "and any required corrections\n\n"
            f"Task:\n{context.task}\n\n"
            f"Proposed implementation:\n{context.previous_output}"
        )

        response = await self.model.generate(prompt)
        data = json.loads(response)

        if not isinstance(data, dict):
            raise ValueError("Review response must be a JSON object")

        if type(data.get("approved")) is not bool:
            raise ValueError("Review approved must be a boolean")

        if not isinstance(data.get("feedback"), str):
            raise ValueError("Review feedback must be a string")

        return ReviewResult(
            approved=data["approved"],
            feedback=data["feedback"],
        )
