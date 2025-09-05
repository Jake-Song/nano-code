"""Main CLI entry point for nano-code agent."""

import click
from rich.console import Console
from rich.panel import Panel
from nano_code.agent import CodingAgent

console = Console()


@click.group()
@click.version_option()
def main():
    """A simple coding agent CLI for analyzing and generating code."""
    pass


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
def analyze(file_path):
    """Analyze a code file and provide insights."""
    agent = CodingAgent()
    
    try:
        result = agent.analyze_file(file_path)
        console.print(Panel(result, title=f"Analysis of {file_path}", border_style="blue"))
    except Exception as e:
        console.print(f"[red]Error analyzing file: {e}[/red]")


@main.command()
@click.option('--language', '-l', default='python', help='Programming language')
@click.option('--output', '-o', help='Output file path')
@click.argument('description')
def generate(description, language, output):
    """Generate code based on a description."""
    agent = CodingAgent()
    
    try:
        code = agent.generate_code(description, language)
        
        if output:
            with open(output, 'w') as f:
                f.write(code)
            console.print(f"[green]Code generated and saved to {output}[/green]")
        else:
            console.print(Panel(code, title=f"Generated {language} code", border_style="green"))
    except Exception as e:
        console.print(f"[red]Error generating code: {e}[/red]")


@main.command()
def chat():
    """Start an interactive chat session with the coding agent."""
    agent = CodingAgent()
    console.print(Panel("Welcome to nano-code interactive mode! Type 'exit' to quit.", 
                       title="Nano Code Agent", border_style="cyan"))
    
    while True:
        try:
            user_input = input("\n🤖 > ")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                console.print("[yellow]Goodbye![/yellow]")
                break
                
            if not user_input.strip():
                continue
                
            response = agent.chat(user_input)
            console.print(f"[cyan]{response}[/cyan]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    main()