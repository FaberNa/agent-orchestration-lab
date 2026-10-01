import pytest

from agent_lab.agents.developer import DeveloperAgent
from agent_lab.models.fake import FakeModelProvider


@pytest.mark.asyncio
async def test_developer_agent_returns_model_response():
    model = FakeModelProvider(response="Proposed implementation")
    agent = DeveloperAgent(model=model)

    result = await agent.run("Implement user authentication")

    assert result == "Proposed implementation"

    assert model.last_prompt is not None
    assert "software developer agent" in model.last_prompt
    assert "Implement user authentication" in model.last_prompt