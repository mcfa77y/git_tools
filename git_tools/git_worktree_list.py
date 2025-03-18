# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "inquirerpy",
#     "loguru",
# ]
# ///
import json
import os
from typing import List

import click
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from git_tool_constants import (
    BUILD_FN,
    DIR_CHOICES,
    GIT_DIR,
    PROFILE_DEFAULT_DIR,
    ROOT_DIR,
)
from utils import prompt_fzf_directory
from worktree_jl import create_choices_for_worktrees


@click.command()
@click.option(
    "--directory",
    default=".",
    help="Directory to execute the git command in",
    type=click.Path(exists=True),
)
def main(directory):
    print(f"[worktree list] directory: {directory}")
    """Main function to list git worktrees and allow selection."""
    worktrees_choices = create_choices_for_worktrees(directory)

    if not worktrees_choices or len(worktrees_choices) == 0:
        print("No git worktrees found.")
        return
    worktree_to_directory = get_worktree_to_directory(worktrees_choices)

    # InquirerPy uses a different syntax for prompts
    selected_worktree = inquirer.fuzzy(
        message="Which git worktree do you want to switch to?",
        choices=worktrees_choices,
    ).execute()
    print(f"Selected worktree: {selected_worktree}")

    directory = prompt_fzf_directory(
        default_choice=worktree_to_directory[selected_worktree],
        dir_choices=DIR_CHOICES,
        root_dir=ROOT_DIR,
    )

    # update the worktree to directory mapping
    worktree_to_directory[selected_worktree] = directory
    with open(WORKTREE_TO_DIRECTORY_URI, "w", encoding="utf-8") as f:
        # write the dictionary as json to the file
        f.write(json.dumps(worktree_to_directory))

    # Run the build function for profile
    BUILD_FN(f"{selected_worktree}/{directory}", GIT_DIR)


WORKTREE_TO_DIRECTORY_URI = "worktree_to_directory.json"


def initialize_worktree_to_directory(worktrees_choices: List[Choice]):
    initial_worktree_to_directory = {}
    # Iterate over each of the choices and map the value to a default directory
    for choice in worktrees_choices:
        initial_worktree_to_directory[choice.value] = PROFILE_DEFAULT_DIR
    with open(WORKTREE_TO_DIRECTORY_URI, "w", encoding="utf-8") as f:
        # write the dictionary as json to the file
        f.write(json.dumps(initial_worktree_to_directory))
    return initial_worktree_to_directory


def update_worktree_to_directory(worktrees_choices: List[Choice]):
    with open(WORKTREE_TO_DIRECTORY_URI, "r", encoding="utf-8") as f:
        worktree_to_directory = json.load(f)
    # if worktree_choices is not in worktree_to_directory then add it and set it to default directory and update file
    for choice in worktrees_choices:
        if choice.value not in worktree_to_directory:
            print(f"[worktree list] add {choice.value} to {WORKTREE_TO_DIRECTORY_URI}")
            worktree_to_directory[choice.value] = PROFILE_DEFAULT_DIR
    # if worktree_to_directory is not in worktree_choices then remove it and update file
    worketree_to_directory_keys_to_delete = []
    for worktree in worktree_to_directory:
        if worktree not in [choice.value for choice in worktrees_choices]:
            print(f"[worktree list] remove {worktree} from {WORKTREE_TO_DIRECTORY_URI}")
            worketree_to_directory_keys_to_delete.append(worktree)
    for worktree in worketree_to_directory_keys_to_delete:
        worktree_to_directory.pop(worktree)
    with open(WORKTREE_TO_DIRECTORY_URI, "w", encoding="utf-8") as f:
        f.write(json.dumps(worktree_to_directory))
    return worktree_to_directory


def get_worktree_to_directory(worktrees_choices: List[Choice]):
    # Create a json file if it does not exist for saving the preference of a directory to a worktree
    if not os.path.exists(WORKTREE_TO_DIRECTORY_URI):
        print(f"[worktree list] create {WORKTREE_TO_DIRECTORY_URI}")
        worktree_to_directory = initialize_worktree_to_directory(worktrees_choices)
    else:
        print(f"[worktree list] read {WORKTREE_TO_DIRECTORY_URI}")
        worktree_to_directory = update_worktree_to_directory(
            worktrees_choices=worktrees_choices
        )
    return worktree_to_directory


if __name__ == "__main__":
    main()
