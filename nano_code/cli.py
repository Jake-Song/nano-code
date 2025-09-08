"""Main CLI entry point for nano-code agent."""

import typer
import yaml
from pathlib import Path
from typing import Any
import traceback
from rich.console import Console
from nano_code.chat_agent import ChatAgent
from nano_code.local import LocalEnvironment
from nano_code import global_config_dir
from nano_code.utils.save import save_traj
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession

DEFAULT_OUTPUT = global_config_dir / "last_nano_code_run.traj.json"
console = Console(highlight=False)
app = typer.Typer(rich_markup_mode="rich")

# Create a simple history file in the current directory
prompt_session = PromptSession(history=FileHistory(global_config_dir / "nano_code_task_history.txt"))

@app.command(help="Run the nano-code agent")
def main(
    task: str | None = typer.Option(None, "-t", "--task", help="Task/problem statement", show_default=True),
    output: Path | None = typer.Option(DEFAULT_OUTPUT, "-o", "--output", help="Output trajectory file"),
) -> Any:
    
    config_path = Path(__file__).parent / "default.yaml"
    config = yaml.safe_load(config_path.read_text())

    if not task:
        console.print("[bold yellow]What do you want to do?")
        task = prompt_session.prompt(
            "",
            multiline=True,
            bottom_toolbar=HTML(
                "Submit task: <b fg='yellow' bg='black'>Esc+Enter</b> | "
                "Navigate history: <b fg='yellow' bg='black'>Arrow Up/Down</b> | "
                "Search history: <b fg='yellow' bg='black'>Ctrl+R</b>"
            ),
        )
        console.print("[bold green]Got that, thanks![/bold green]")

    env = LocalEnvironment(**config.get("env", {}))
    agent = ChatAgent(env, **config.get("agent", {}))

    exit_status, result, extra_info = None, None, None
    try:
        exit_status, result = agent.run(task)  
    except Exception as e:
        print(f"Error running agent: {e}", exc_info=True)
        exit_status, result = type(e).__name__, str(e)
        extra_info = {"traceback": traceback.format_exc()}
    finally:
        if output:
            save_traj(agent, output, exit_status=exit_status, result=result, extra_info=extra_info)
    return agent

if __name__ == "__main__":
    app()