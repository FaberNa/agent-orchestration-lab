import asyncio
import pytest

from agent_lab.agents.developer import DeveloperAgent
from agent_lab.agents.reviewer import ReviewerAgent
from agent_lab.models.fake import FakeModelProvider
from agent_lab.orchestration.orchestrator import AgentOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_passes_proposal_to_reviewer():
    developer_model = FakeModelProvider(
        response="Propongo una funzione che somma due numeri."
    )
    reviewer_model = FakeModelProvider(
        response="La proposta soddisfa il task."
    )

    orchestrator = AgentOrchestrator(
        developer=DeveloperAgent(developer_model),
        reviewer=ReviewerAgent(reviewer_model),
    )


    result = await orchestrator.run(
        "Implementa una funzione che somma due numeri."
    )

    assert reviewer_model.last_prompt is not None
    assert developer_model.response in reviewer_model.last_prompt
    assert result.task == "Implementa una funzione che somma due numeri."
    assert result.proposal == developer_model.response
    assert result.review == reviewer_model.response


    print("Risultato:")
    print(result)
    print("\nPrompt ricevuto dal reviewer:")
    print(reviewer_model.last_prompt)

