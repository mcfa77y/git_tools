import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import click
import pretty_errors
from alive_progress import alive_bar
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from list_git_work_tree import create_choices_for_worktrees
from utils import run_command


def remove_working_tree(tree_path):
    """Remove the specified working tree."""
    run_command(f'cd {tree_path} && git worktree remove {tree_path} --force')
    print(f"Removed working tree at '{tree_path}'!")


@click.command()
@click.option('--directory',
              default='.',
              help='Directory to execute the git command in')
def main(directory):
    """
    Allows user to interactively select a working tree to remove.

    Args:
        directory (str): The directory to execute the git command in. Defaults to '.'.

    Returns:
        None
    """
    workingtree_choices = create_choices_for_worktrees(directory)
    selected_trees = inquirer.checkbox(
        message="Which working trees do you want to remove?",
        choices=workingtree_choices,
    ).execute()

    if not selected_trees:
        print("No working trees selected. Exiting.")
        return

    confirm = inquirer.confirm(
        message="Do you really want to remove the selected working trees?"
    ).execute()

    if confirm:
        with ThreadPoolExecutor() as executor:
            tasks = [
                executor.submit(remove_working_tree, tree_choice)
                for tree_choice in selected_trees
            ]
            with alive_bar(len(tasks)) as update_progress_bar:
                for _ in as_completed(tasks):
                    update_progress_bar()
    else:
        print("Aborted!")


if __name__ == "__main__":
    main()
