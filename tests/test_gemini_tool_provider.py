from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from google.genai import types

from agent_lab.models.gemini_tool_provider import GeminiToolProvider
from agent_lab.tools.read_file import ReadFileTool


@pytest.mark.asyncio
async def test_provider_returns_file_content_to_model(tmp_path):
    code = "def divide(a, b):\n    return a / b\n"
    (tmp_path / "calculator.py").write_text(code, encoding="utf-8")

    # Prima risposta: il modello richiede la lettura.
    tool_request = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name="read_file",
                            args={"path": "calculator.py"},
                        )
                    ],
                )
            )
        ]
    )

    # Seconda chiamata: controlliamo cosa riceve il modello.
    async def generate_content(**kwargs):
        if client.models.generate_content.await_count == 1:
            return tool_request

        history = kwargs["contents"]

        assert history[1].role == "model"

        tool_result = history[2].parts[0].function_response
        assert tool_result.name == "read_file"
        assert tool_result.response["content"] == code

        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role="model",
                        parts=[
                            types.Part.from_text(
                                text="Aggiungi un controllo sul divisore zero."
                            )
                        ],
                    )
                )
            ]
        )

    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=AsyncMock(side_effect=generate_content)
        )
    )

    provider = GeminiToolProvider(
        client=client,
        model="test-model",
        reader=ReadFileTool(tmp_path),
    )

    result = await provider.generate("Analizza calculator.py")

    assert result == "Aggiungi un controllo sul divisore zero."
    assert client.models.generate_content.await_count == 2

@pytest.mark.asyncio
async def test_provider_reports_error_for_file_outside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Il file esiste, ma fuori dalla cartella consentita.
    outside_file = tmp_path / "private.py"
    outside_file.write_text(
        "PRIVATE_CONTENT = 'must not reach the model'",
        encoding="utf-8",
    )

    tool_request = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name="read_file",
                            args={"path": "../private.py"},
                        )
                    ],
                )
            )
        ]
    )

    async def generate_content(**kwargs):
        if client.models.generate_content.await_count == 1:
            return tool_request

        history = kwargs["contents"]
        tool_result = history[2].parts[0].function_response

        assert tool_result.name == "read_file"
        assert "error" in tool_result.response
        assert "content" not in tool_result.response
        assert "must not reach the model" not in str(history)

        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role="model",
                        parts=[
                            types.Part.from_text(
                                text="Non posso leggere il file richiesto."
                            )
                        ],
                    )
                )
            ]
        )

    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=AsyncMock(side_effect=generate_content)
        )
    )

    provider = GeminiToolProvider(
        client=client,
        model="test-model",
        reader=ReadFileTool(workspace),
    )

    result = await provider.generate("Analizza ../private.py")

    assert result == "Non posso leggere il file richiesto."
    assert client.models.generate_content.await_count == 2


@pytest.mark.asyncio
async def test_provider_continues_after_tool_error(tmp_path):
    code = "def divide(a, b):\n   return a / b\n"
    (tmp_path / "calculator.py").write_text(code, encoding="utf-8")

    def request_file(path):
        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role="model",
                        parts=[
                            types.Part.from_function_call(
                                name="read_file",
                                args={"path": path},
                            )
                        ],
                    )
                )
            ]
        )

    async def generate_content(**kwargs):
        call_number = client.models.generate_content.await_count
        history = kwargs["contents"]

        if call_number == 1:
            return request_file("../calculator.py")

        if call_number == 2:
            tool_result = history[-1].parts[0].function_response
            assert "error" in tool_result.response

            return request_file("calculator.py")

        tool_result = history[-1].parts[0].function_response
        assert tool_result.response["content"] == code

        return types.GenerateContentResponse(
            candidates=[
                types.Candidate(
                    content=types.Content(
                        role="model",
                        parts=[
                            types.Part.from_text(
                                text="Gestisci il caso b == 0."
                            )
                        ],
                    )
                )
            ]
        )

    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=AsyncMock(side_effect=generate_content)
        )
    )

    provider = GeminiToolProvider(
        client=client,
        model="test-model",
        reader=ReadFileTool(tmp_path),
    )

    result = await provider.generate("Analizza calculator.py")

    assert result == "Gestisci il caso b == 0."
    assert client.models.generate_content.await_count == 3

@pytest.mark.asyncio
async def test_provider_stops_when_model_keeps_requesting_tools(tmp_path):
    (tmp_path / "calculator.py").write_text(
        "def divide(a, b):\n    return a / b\n",
        encoding="utf-8",
    )

    tool_request = types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name="read_file",
                            args={"path": "calculator.py"},
                        )
                    ],
                )
            )
        ]
    )

    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=AsyncMock(return_value=tool_request)
        )
    )

    provider = GeminiToolProvider(
        client=client,
        model="test-model",
        reader=ReadFileTool(tmp_path),
    )

    with pytest.raises(
            RuntimeError,
            match="Model step limit reached without a final answer",
    ):
        await provider.generate("Analizza calculator.py")

    assert client.models.generate_content.await_count == 4