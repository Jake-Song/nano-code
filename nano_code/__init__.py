"""A simple coding agent CLI."""

import os
from pathlib import Path
from typing import Any, Protocol

__version__ = "0.1.0"
global_config_dir = Path.home() / ".config" / "nano-code"
global_config_dir.mkdir(parents=True, exist_ok=True)


# === Protocols ===
# You can ignore them unless you want static type checking.

class Model(Protocol):
    """Protocol for language models."""

    config: Any
    cost: float
    n_calls: int

    def query(self, messages: list[dict[str, str]], **kwargs) -> dict: ...

    def get_template_vars(self) -> dict[str, Any]: ...


class Environment(Protocol):
    """Protocol for execution environments."""

    config: Any

    def execute(self, command: str, cwd: str = "") -> dict[str, str]: ...

    def get_template_vars(self) -> dict[str, Any]: ...


class Agent(Protocol):
    """Protocol for agents."""

    model: Model
    env: Environment
    messages: list[dict[str, str]]
    config: Any

    def run(self, task: str, **kwargs) -> tuple[str, str]: ...