import rich
import typer
from typing_extensions import Annotated

from ai_commit import git_integration, llm_provider, prompt_manager, service

app = typer.Typer()

class OllamaProvider(llm_provider.LLMProvider):
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        rich.print(
            "[bold red]Error: Real Ollama provider is not implemented yet.[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def main(
    style: Annotated[
        str,
        typer.Option(
            help="The prompt style to use (e.g., 'conventional', 'pirate')."
        ),
    ] = "conventional",
    print_commit: Annotated[
        bool,
        typer.Option(
            "--print", help="Print the generated commit message to the console."),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Run in dry-run mode using a mock LLM provider.",
        ),
    ] = False,
):
    """
    Generates an AI-powered commit message for your staged changes.
    """
    try:
        provider: llm_provider.LLMProvider
        if dry_run:
            provider = llm_provider.MockProvider()
            rich.print(
                "[bold yellow]Dry run mode: Using Mock LLM Provider.[/bold yellow]")
        else:
            provider = OllamaProvider() # Placeholder for now

        diff = git_integration.get_staged_diff()
        rich.print("Generating commit message...")

        commit_message = service.generate_commit(
            diff=diff,
            style=style,
            provider=provider
        )

        if print_commit:
            rich.print("\n[bold green]Generated Commit Message:[/bold green]")
            rich.print(f"[cyan]{commit_message}[/cyan]")
        else:
            rich.print(
                "[yellow]--print flag was used. In the future, "
                "this would commit.[/yellow]")

    except git_integration.NoStagedChanges as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        available = prompt_manager.list_styles()
        rich.print(f"Please choose from available styles: {available}")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)
