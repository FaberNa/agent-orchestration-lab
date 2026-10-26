# Agent Orchestration Lab

A step-by-step lab for learning agent orchestration in Python, starting with two LLM roles and building toward a workflow with tools, review, and file generation.

The project makes the mechanics visible: who decides the next step, what data the model receives, and which rules our code enforces. It is a learning project, not a production platform.

## Before you start: what is an agent here?

The developer and reviewer are local Python objects. They construct prompts and call a model provider, which can use a remote model or simulated responses in tests. In the live example, both use Gemini with different instructions and configurations; they do not have to be different models.

The orchestrator is ordinary code: it controls call order, passes context, acts on approval, and limits attempts. The model produces proposals, makes review judgments, and chooses file-reading requests.

A single LLM call may be enough for a simple task. This lab introduces complexity gradually to explore when actions and feedback help; it does not assume that adding agents always improves results.

## Setup

You need Python 3.12 or later. Only the live examples require a Gemini API key with access to your chosen model. Run all commands from the repository root. Shell examples target macOS/Linux.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

The commands below explicitly set `PYTHONPATH=src` to make the `agent_lab` package available.

## 1. Understand the workflow without calling an API

Start with these files:

- [AgentContext](src/agent_lab/agents/context.py): the task, previous output, and feedback passed to an agent.
- [DeveloperAgent](src/agent_lab/agents/developer.py): builds the development prompt, including the previous proposal and feedback when available.
- [ReviewerAgent](src/agent_lab/agents/reviewer.py): builds the review prompt and parses the JSON response.
- [ReviewResult](src/agent_lab/agents/review.py): holds `approved` and `feedback`.
- [AgentOrchestrator](src/agent_lab/orchestration/orchestrator.py): coordinates the two agents.
- [OrchestrationResult](src/agent_lab/orchestration/result.py): returns the task, latest proposal, and latest review.

```text
Task → Developer → proposal → Reviewer
           ↑                    |
           └── proposal + feedback on rejection
                                |
                    approval or attempt limit
                                ↓
                       OrchestrationResult
```

The reviewer delegates approval to the model, which reads the task and proposal. Python validates the response fields and acts on the result; it does not independently determine whether the code is correct. Valid JSON and `approved=True` do not prove that the solution works.

With `max_attempts=3`, the orchestrator allows up to three developer/reviewer rounds. A rejection prepares new context for the developer; approval ends the loop. If the final review still rejects the proposal, the result is returned with `approved=False`. A provider exception instead interrupts execution.

Run the orchestrator tests:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_orchestrator.py -v
```

[FakeModelProvider](src/agent_lab/models/fake.py) and mocks return predefined responses. These tests require no keys, network, or API credits. They check how our program responds to those inputs.

## 2. Connect a real model

[ModelProvider](src/agent_lab/models/base.py) defines the asynchronous contract `generate(prompt) -> str`. The repository includes fake, OpenAI, and Gemini providers. The current example script uses Gemini; the OpenAI provider is available, but the script does not expose an environment setting to switch providers.

Create `.env` in the repository root:

```dotenv
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=AN_ACCESSIBLE_MODEL_ID
```

Get your key from [Google AI Studio](https://aistudio.google.com/apikey). Choose an ID from the [Gemini model catalog](https://ai.google.dev/gemini-api/docs/models) and check your project's quotas and terms on the [pricing page](https://ai.google.dev/gemini-api/docs/pricing). The example has been run with `gemini-3.5-flash-lite`; availability and quotas may change.

Git already ignores `.env`. Verify this without displaying its contents:

```bash
git check-ignore .env
```

The scripts load the file through `python-dotenv`; existing environment variables take precedence. Keep keys out of source files, tests, and commits.

Start with a minimal request:

```bash
PYTHONPATH=src .venv/bin/python src/examples/check_gemini.py
```

The script prints the model ID and asks it to answer `OK`. This is a real API call: it uses your project's quota and may incur charges. The current code uses a 20-second timeout, although the timeout message still says 60 seconds.

## 3. Understand tool calling

The developer can request `read_file(path)`. The model produces a function name and arguments; our Python code validates and performs the read. The model does not directly access the filesystem.

```text
Developer → GeminiToolProvider → model
                                  |
                      read_file("calculator.py") request
                                  ↓
                              ReadFileTool
                                  |
                            content or error
                                  ↓
                    next model call with conversation history
                                  |
                       answer or another tool request
```

Read [GeminiToolProvider](src/agent_lab/models/gemini_tool_provider.py) to follow the loop. Automatic SDK tool execution is disabled: the program explicitly handles requests and results. The conversation also preserves the model's original response.

[ReadFileTool](src/agent_lab/tools/read_file.py) accepts relative paths to `.py` files inside the authorized directory, up to 20,000 characters. It resolves paths, including symbolic links, before checking the directory boundary. Expected reading errors are returned to the model, which can make another request.

The provider allows four model responses per `generate`, including the final answer, with a 60-second timeout per call. If the model never concludes, it raises an error. This limit is separate from the orchestrator's three attempts.

The directory boundary checks access permission, not task adherence: the model could request a different file from the one the user intended, as long as it is allowed. File contents are transmitted to the remote service; keep only data intended for this exercise in the workspace.

Test the mechanism without API calls:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_gemini_tool_provider.py -v
```

These tests simulate model decisions but perform real reads in temporary directories. They cover allowed reads, rejection outside the workspace, recovery after a tool error, and termination at the step limit. They do not measure the quality of AI reasoning.

## 4. Run the live workflow and save the proposal

[run_orchestration.py](src/examples/run_orchestration.py) assembles the components:

- The developer uses `GeminiToolProvider` with access to `workspace`.
- The reviewer uses `GeminiModelProvider` with a JSON schema for `approved` and `feedback`.
- The orchestrator runs the review loop.
- If the final proposal is approved, the script checks its syntax with `ast.parse` and overwrites `workspace/calculator.py`.

Run:

```bash
PYTHONPATH=src .venv/bin/python src/examples/run_orchestration.py
```

The console shows attempts, model steps, and requested file reads. Results depend on the model: immediate approval and a fixed number of calls are not guaranteed.

The task is currently hardcoded in the script. It requests plain Python code for a `divide(a, b)` function that raises `ValueError` when `b` is zero. The prompt still includes the historical result `3 passed, 1 failed`: this is manually supplied feedback, not a fresh measurement on every run. Update that text if you change the exercise.

The script controls writing to a fixed path; the model has no write tool. `ast.parse` checks syntax without executing the code or guaranteeing correctness or safety. The reviewer does not independently read the file or execute tests: it evaluates the task and proposal it receives.

## 5. Verify the correction with independent tests

The exercise includes [calculator.py](workspace/calculator.py) and [four tests](workspace/test_calculator.py) written independently of the model's proposal: ordinary division, negative numbers, a zero numerator, and a zero divisor.

Inspect the generated file first, then run locally:

```bash
PYTHONPATH=workspace .venv/bin/python -m pytest workspace/test_calculator.py -q
```

The corrected version should produce `4 passed`. To reproduce the initial failure, temporarily use this implementation while keeping the tests unchanged:

```python
def divide(a, b):
    return a / b
```

This should produce `3 passed, 1 failed`: Python raises `ZeroDivisionError`, while the contract requires `ValueError`. Running the workflow again lets the developer propose a correction and the script save it; you can then verify it with pytest.

Local execution imports and runs generated code, so this exercise requires manual inspection of the file. Automatic execution in an isolated container is a future step, not an existing feature.

## Command reference

Lab tests only, without API calls:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/ -q
```

Calculator exercise only, without API calls but executing the local file:

```bash
PYTHONPATH=workspace .venv/bin/python -m pytest workspace/test_calculator.py -q
```

Both groups:

```bash
PYTHONPATH=src:workspace .venv/bin/python -m pytest tests/ workspace/ -q
```

To display a test's `print` output:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_orchestrator.py -v -s
```

## Troubleshooting from the lab

| Symptom | What to check |
| --- | --- |
| `No module named 'src'` | Imports start with `agent_lab`, not `src.agent_lab`; run from the root with `PYTHONPATH=src`. |
| Missing configuration | Check `.env` in the root, variable names, and any values already exported in your terminal. |
| Model returns `404 NOT_FOUND` | A catalog entry does not guarantee generation access: read the API message and check your project. |
| `503 UNAVAILABLE` | The service reports unavailability; avoid parallel reruns. The SDK may already retry requests. |
| Timeout | This alone does not establish a credit issue: start with the minimal request in `check_gemini.py`. |
| `JSONDecodeError` during review | Check that the reviewer uses the provider with the JSON schema configured in the example script. |
| `SyntaxError` before saving | The proposal is not valid Python, for example because it contains Markdown. The file is not written. |
| OpenAI `credit_balance_exhausted` | The request reports an exhausted API balance; a tier name does not imply available credit. |

## What comes next

The next goal is to close the verification loop: save a proposal in a dedicated environment, run tests with isolation and a timeout, collect the actual outcome, and return failures to the developer. Review judgments will remain separate from test results.

There is currently no Docker runner, automatic test execution in the orchestrator, persistent memory, exposed application API, or quality/cost measurement. The `api` directory is only a placeholder. Before adding more agents, the lab should compare the correction loop with a single call to determine whether the added complexity delivers a measurable benefit.
