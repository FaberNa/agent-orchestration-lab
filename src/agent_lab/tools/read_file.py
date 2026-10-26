from pathlib import Path


class ReadFileTool:
    """Reads Python files inside a dedicated workspace."""

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def read_file(self, path: str) -> str:
        """Read a Python file using a path relative to the workspace."""
        relative_path = Path(path)

        if relative_path.is_absolute():
            raise ValueError("Use a path relative to the workspace")

        target = (self.workspace / relative_path).resolve()

        if not target.is_relative_to(self.workspace):
            raise ValueError("File outside the allowed workspace")

        if target.suffix != ".py":
            raise ValueError("Only Python files are supported")

        with target.open("r", encoding="utf-8") as file:
            content = file.read(20_001)

        if len(content) > 20_000:
            raise ValueError("File exceeds the 20,000 character limit")

        return content