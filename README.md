# AI-Commit

`ai-commit` is a command-line tool that uses local AI models via Ollama to automatically generate commit messages for your staged changes.

## Features

-   **AI-Powered Messages**: Generates conventional commit messages from your git diff.
-   **Interactive Workflow**: Review, edit, or accept the generated message before committing.
-   **Customizable Styles**: Easily define new prompt styles (e.g., "pirate", "ghanaian").
-   **Git Hooks**: Automate the process to run on every `git commit`.
-   **Local First**: Works with your local Ollama instance, keeping your code private.


## Installation

```bash
pip install ai-commit
```

## Usage
1. Basic Workflow

The main command requires a --live or --dry-run flag.

- Stage your changes: git add .
- Run the command in live mode:
    
```bash
   ai-commit --live
```

- You will be prompted to [Y]es, [n]o, or [e]dit the generated message.