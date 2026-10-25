import asyncio
import pytest
from unittest.mock import AsyncMock


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
        response='{"approved": true, "feedback": "La proposta soddisfa il task."}'
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
    assert result.review.approved is True
    assert result.review.feedback == "La proposta soddisfa il task."


    print("Risultato:")
    print(result)
    print("\nPrompt ricevuto dal reviewer:")
    print(reviewer_model.last_prompt)

@pytest.mark.asyncio
async def test_orchestrator_revises_proposal_after_rejection():
    task = "Implementa una funzione di divisione."
    first_proposal = "return a / b"
    revised_proposal = "if b == 0: raise ValueError; return a / b"
    feedback = "Gestisci la divisione per zero."

    developer_model = FakeModelProvider()
    developer_model.generate = AsyncMock(
        side_effect=[first_proposal, revised_proposal]
    )

    reviewer_model = FakeModelProvider()
    reviewer_model.generate = AsyncMock(
        side_effect=[
            '{"approved": false, "feedback": "Gestisci la divisione per zero."}',
            '{"approved": true, "feedback": "La proposta è corretta."}',
        ]
    )

    orchestrator = AgentOrchestrator(
        developer=DeveloperAgent(developer_model),
        reviewer=ReviewerAgent(reviewer_model),
        max_attempts=3,
    )

    result = await orchestrator.run(task)

    assert result.task == task
    assert result.proposal == revised_proposal
    assert result.review.approved is True

    assert developer_model.generate.await_count == 2
    assert reviewer_model.generate.await_count == 2

    second_developer_prompt = (
        developer_model.generate.await_args_list[1].args[0]
    )
    assert task in second_developer_prompt
    assert first_proposal in second_developer_prompt
    assert feedback in second_developer_prompt

    second_reviewer_prompt = (
        reviewer_model.generate.await_args_list[1].args[0]
    )
    assert revised_proposal in second_reviewer_prompt

@pytest.mark.asyncio
async def test_orchestrator_stops_after_max_attempts():
    developer_model = FakeModelProvider(response="Proposta da correggere")
    reviewer_model = FakeModelProvider(
        response='{"approved": false, "feedback": "Correggi la proposta."}'
    )

    developer_model.generate = AsyncMock(
        wraps=developer_model.generate
    )
    reviewer_model.generate = AsyncMock(
        wraps=reviewer_model.generate
    )

    orchestrator = AgentOrchestrator(
        developer=DeveloperAgent(developer_model),
        reviewer=ReviewerAgent(reviewer_model),
        max_attempts=3,
    )

    result = await orchestrator.run("Implementa una divisione.")

    assert developer_model.generate.await_count == 3
    assert reviewer_model.generate.await_count == 3
    assert result.proposal == "Proposta da correggere"
    assert result.review.approved is False
    assert result.review.feedback == "Correggi la proposta."