import pytest

from agent_lab.models.fake import FakeModelProvider


@pytest.mark.asyncio
async def test_fake_model_provider_returns_configured_response():
    model = FakeModelProvider(response="Hello from fake model")

    result = await model.generate("Hello")

    assert result == "Hello from fake model"