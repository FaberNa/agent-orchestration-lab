import pytest

from agent_lab.agents.reviewer import ReviewerAgent
from agent_lab.agents.context import AgentContext
from agent_lab.models.fake import FakeModelProvider

@pytest.mark.asyncio
async def test_reviewer_agent_returns_model_response():
    model = FakeModelProvider(
        response='{"approved": true, "feedback":"Review of the proposed implementation"}'
    )
    agent = ReviewerAgent(model=model)

    context = AgentContext(
        task="Review user authentication implementation",
        previous_output="Use password hashing and session cookies.",
    )
    result = await agent.run(context)

    assert result.feedback == "Review of the proposed implementation"

    assert model.last_prompt is not None
    assert "software reviewer agent" in model.last_prompt
    assert "Review user authentication implementation" in model.last_prompt
    assert context.previous_output in model.last_prompt
    assert result.approved is True

