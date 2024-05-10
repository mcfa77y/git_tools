import os

import click
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
    new_worktree_dir = f"{WORKTREE_DIR}/{branch_name}"
    print(f"[worktree add] git worktree add {new_worktree_dir}")
    run_command(f"git worktree add {new_worktree_dir} {branch_name}")
    os.chdir(f"{new_worktree_dir}")
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


ADD_WORKTREE = "Add Worktree"
CHECKOUT_BRANCH = "Checkout Branch"
ACTIONS = [ADD_WORKTREE, CHECKOUT_BRANCH]


@click.command()
@click.option('--action', default='', help='What do you want to do?', )
@click.option('--directory',
              default='',
              help='Directory to execute the git command in')
def main(action, directory):
    if action == '':
        answers = prompt([{
            'type': 'list',
            'name': 'action',
            'message': "What do you want to do?",
            'default': ADD_WORKTREE,
            'choices': ACTIONS
        }])
    else:
        answers = {'action': action}

    if directory == '':
        directory = prompt_fzf_directory()

    branch_name = prompt_fzf_git_branches()
    if answers['action'] == 'Checkout Branch':
        common_checkout_branch(branch_name, directory)
    elif answers['action'] == 'Add Worktree':
        common_worktree_add(branch_name, directory)


if __name__ == "__main__":
    print(f"[worktree add] fetch {NEATLEAF_DIR}")
    os.chdir(NEATLEAF_DIR)
    run_command("git fetch --prune")
    main()
