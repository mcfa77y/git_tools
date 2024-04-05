import os

import click
import pretty_errors
from InquirerPy import inquirer, prompt

from utils import prompt_fzf_directory, run_command
from WorktreeJL import create_choices_for_worktrees


@click.command()
@click.option('--directory',
              default='.',
              help='Directory to execute the git command in',
              type=click.Path(exists=True))
def main(directory):
    """Main function to list git worktrees and allow selection."""
    worktrees = create_choices_for_worktrees(directory)

    if not worktrees or len(worktrees) == 0:
        print("No git worktrees found.")
        return

    # InquirerPy uses a different syntax for prompts
    selected_worktree = inquirer.fuzzy(
        message="Which git worktree do you want to switch to?",
        choices=worktrees).execute()
    print(f'Selected worktree: {selected_worktree}')

    directory = prompt_fzf_directory()

    # Change to the selected directory
    os.chdir(f'{selected_worktree}/{directory}')
    run_command("code .")
    run_command("yarn")


if __name__ == "__main__":
    main()
