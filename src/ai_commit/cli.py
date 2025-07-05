import asyncio
import os
import subprocess
import tempfile

import rich
import typer
from rich.prompt import Prompt
from typing_extensions import Annotated

from ai_commit import (
    git_integration,
    hook_manager,
    llm_provider,
    prompt_manager,
    service,
)

app = typer.Typer()


def _handle_edit_flow(initial_message: str) -> str:
    """Handles the logic for editing a message in an external editor."""
    editor = os.environ.get("EDITOR")
    if not editor:
        rich.print("[bold red]Error: EDITOR environment variable not set.[/bold red]")
        raise typer.Exit(code=1)

    # Use a temporary file for the user to edit
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as tf:
        tf.write(initial_message)
        temp_file_path = tf.name

    try:
        # Open the file in the user's specified editor
        subprocess.run([editor, temp_file_path], check=True)
        # Read the potentially modified content
        with open(temp_file_path) as tf:
            edited_message = tf.read().strip()
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

    return edited_message if edited_message else initial_message


async def _run_interactive_flow(style: str, provider: llm_provider.LLMProvider):
    """Contains the core async logic for the interactive session."""
    diff = git_integration.get_staged_diff()
    rich.print("Generating commit message...")
    commit_message = await service.generate_commit(
        diff=diff, style=style, provider=provider
    )

    while True:
        rich.print("\n[bold green]Generated Commit Message:[/bold green]")
        rich.print(f"[cyan]{commit_message}[/cyan]\n")
        choice = Prompt.ask(
            "[bold]Commit with this message? [/bold]",
            choices=["y", "n", "e"],
            default="y"
        ).lower()
        if choice == 'y':
            git_integration.commit(commit_message)
            rich.print("[bold green]✔ Commit successful![/bold green]")
            break
        elif choice == 'e':
            commit_message = _handle_edit_flow(commit_message)
        else:
            rich.print("[yellow]Commit aborted.[/yellow]")
            break

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    style: Annotated[
        str,
        typer.Option(
            help="The prompt style to use (e.g., 'conventional', 'ghanaian', 'pirate')."
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
    live: Annotated[
        bool,
        typer.Option("--live",
                     help="Use the real Ollama provider "
                          "(requires Ollama to be running)."),
    ] = False,
):
    """
    Generates an AI-powered commit message for your staged changes.
    """

    if ctx.invoked_subcommand is not None:
        return

    try:
        provider: llm_provider.OllamaProvider()
        if dry_run:
            provider = llm_provider.MockProvider()
            rich.print(
                "[bold yellow]Dry run mode: Using Mock LLM Provider.[/bold yellow]")
        elif live:
            provider = llm_provider.OllamaProvider()
            rich.print("[bold blue]Live mode: Using real Ollama provider.[/bold blue]")
        else:
            rich.print(
                "[bold red]Error:[/bold red] "
                "Please specify either [cyan]--live[/cyan] or [cyan]--dry-run[/cyan].")
            raise typer.Exit(code=1)


        if print_commit:
            diff = git_integration.get_staged_diff()
            commit_message = asyncio.run(service.generate_commit(
                diff=diff, style=style, provider=provider
            ))
            rich.print("\n[bold green]Generated Commit Message:[/bold green]")
            rich.print(f"[cyan]{commit_message}[/cyan]")
            return

        asyncio.run(_run_interactive_flow(style, provider))


    except git_integration.NoStagedChanges as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except KeyError as e:
        rich.print(f"[bold red]Error:[/bold red] {e}")
        available = prompt_manager.list_styles()
        rich.print(f"Please choose from available styles: {available}")
        raise typer.Exit(code=1)
    except llm_provider.OllamaConnectionError as e:
        rich.print(f"[bold red]Ollama Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command(name="install-hook")
def install_hook_command(
    is_global: Annotated[
        bool,
        typer.Option("--global", help="Install the hook globally.")] = False,
):
    """
    Installs the prepare-commit-msg git hook.
    """
    try:
        hook_path = hook_manager.install_hook(is_global)
        rich.print(
            f"[bold green]✔ Hook installed successfully at:[/bold green] {hook_path}")
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)
