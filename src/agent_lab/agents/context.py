from dataclasses import dataclass


@dataclass
class AgentContext:
    """Context passed to an agent during execution."""

    task: str
    previous_output: str | None = None