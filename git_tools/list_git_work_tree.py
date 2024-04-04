import os

import click
import pretty_errors
from InquirerPy import inquirer, prompt

from constants import DIR_CHIOICES
from utils import create_choices_for_worktrees, run_command


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

    answers = prompt({
        'type': 'list',
        'name': 'directory',
        'message': "Which directory do you want to build?",
        'default': 'dashboard',
        'choices': DIR_CHIOICES
    })

    # Change to the selected directory
    os.chdir(f'{selected_worktree}/{answers["directory"]}')
    run_command("code .")
    run_command("yarn")


if __name__ == "__main__":
    main()
