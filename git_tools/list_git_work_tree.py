import os
import subprocess

import click
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import pretty_errors

import subprocess

from utils import list_working_trees, run_command


def get_git_worktrees(directory):
    """Get a list of current git working trees."""
    try:
        worktrees = list_working_trees(directory)

        # Sort worktrees by the URL
        worktrees.sort(key=lambda worktree: worktree.split('/')[-1].lower(),
                       reverse=True)

        # Create choices list
        choices = [
            Choice(value=worktree, name=worktree.split('/')[-1])
            for worktree in worktrees
        ]

        return choices
    except subprocess.CalledProcessError:
        print("Error: Failed to get git worktrees.")
        return []


@click.command()
@click.option('--directory',
              default='.',
              help='Directory to execute the git command in',
              type=click.Path(exists=True))
def main(directory):
    """Main function to list git worktrees and allow selection."""
    worktrees = get_git_worktrees(directory)

    if not worktrees:
        print("No git worktrees found.")
        return

    # InquirerPy uses a different syntax for prompts
    selected_worktree = inquirer.fuzzy(
        message="Which git worktree do you want to switch to?",
        choices=worktrees).execute()
    print(f'Selected worktree: {selected_worktree}')
    # Change to the selected directory
    run_command(f"echo 'cd {selected_worktree}/dashboard; yarn; ee .; cd -' | pbcopy; pbpaste")
    os.chdir(selected_worktree)
    


if __name__ == "__main__":
    main()
