from abc import ABC, abstractmethod

from agent_lab.models.base import ModelProvider
from agent_lab.agents.context import AgentContext

from src.agent_lab.agents.review import ReviewResult


class Agent(ABC):
    """Base abstraction for an AI agent."""

    def __init__(self, model: ModelProvider):
        self.model = model

    @abstractmethod
    async def run(self, context: AgentContext) -> str | ReviewResult:
        """Execute the agent for the given task."""
        pass