import os

import pretty_errors
from InquirerPy import inquirer, prompt
from InquirerPy.base.control import Choice

from BranchInfoJL import format_branch_info_names, get_branch_info
from constants import NEATLEAF_DIR, WORKTREE_DIR
from utils import prompt_fzf_directory, run_command


def common_checkout_branch(branch_name, directory):
    print("stash")
    run_command("pwd; git stash push")
    print(f"checkout {branch_name}")
    run_command(f"git checkout {branch_name}")
    print("stash pop")
    run_command("git stash pop")
    print(f"{directory} it up")
    os.chdir(directory)
    run_command("yarn")


def copy_husky_dir():
    os.makedirs(".husky/_", exist_ok=True)
    print("[worktree add] copy husky dir")
    run_command(f"cp {NEATLEAF_DIR}/.husky/_/husky.sh .husky/_/")
    # print("[worktree add] create .git dir")
    # os.makedirs(".git", exist_ok=True)


def common_worktree_add(branch_name, directory):
    print(f"[worktree add] git worktree add {WORKTREE_DIR}/{branch_name}")
    run_command(f"git worktree add {WORKTREE_DIR}/{branch_name} {branch_name}")
    os.chdir(f"{WORKTREE_DIR}/{branch_name}")
    copy_husky_dir()
    print("[worktree add] copy envs")
    run_command(f"cp {NEATLEAF_DIR}/dashboard/.env dashboard")
    os.chdir(directory)
    run_command("code .")
    run_command("yarn")


def get_branches_as_choice_list():
    # Run the git branch command
    branches = get_branch_info(NEATLEAF_DIR)
    # sort branches by youngest first
    # branches.sort(key=lambda branch: branch.age, reverse=True)
    branches.sort(key=lambda branch: branch.age_number)
    choices = []
    format_branch_info_names(branches)
    for branch in branches:
        choice = Choice(value=branch.name, name=branch.info)
        choices.append(choice)
    return choices


def prompt_fzf_git_branches() -> str:
    choices = get_branches_as_choice_list()
    # Use inquirer to let the user select a branch
    selected_branch: str = inquirer.fuzzy(message="Select a branch",
                                          choices=choices).execute()

    return selected_branch


def main():
    answers = prompt([{
        'type': 'list',
        'name': 'action',
        'message': "What do you want to do?",
        'default': 'Add Worktree',
        'choices': ['Add Worktree', 'Checkout Branch']
    }])

    directory = prompt_fzf_directory()
    branch_name = prompt_fzf_git_branches()
    if answers['action'] == 'Checkout Branch':
        common_checkout_branch(branch_name, directory)
    elif answers['action'] == 'Add Worktree':
        common_worktree_add(branch_name, directory)


if __name__ == "__main__":
    print(f"[worktree add] fetch {NEATLEAF_DIR}")
    os.chdir(NEATLEAF_DIR)
    print(run_command('pwd'))
    run_command("git fetch --prune")
    main()
