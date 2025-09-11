# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "alive-progress",
#     "click",
#     "loguru",
#     "inquirerpy",
# ]
# ///
from concurrent.futures import ThreadPoolExecutor, as_completed

import click
from alive_progress import alive_bar
from InquirerPy import inquirer

from git_worktree_list import create_choices_for_worktrees
from utils import run_command


def remove_working_tree(tree_path):
    """Remove the specified working tree."""
    run_command(f"cd {tree_path} && git worktree remove {tree_path} --force")
    print(f"Removed working tree at '{tree_path}'!")


@click.command()
@click.option(
    "--directory", default=".", help="Directory to execute the git command in"
)
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
        with alive_bar(len(selected_trees)) as update_progress_bar:
            for tree_choice in selected_trees:
                remove_working_tree(tree_choice)
                update_progress_bar()
    else:
        print("Aborted!")


if __name__ == "__main__":
    main()
