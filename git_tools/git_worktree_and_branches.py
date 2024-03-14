import os
from constants import NEATLEAF_DIR, WORKTREE_DIR
from utils import run_command
import pretty_errors
from InquirerPy import inquirer, prompt 
from InquirerPy.base.control import Choice



def common_checkout_branch(branch_name, directory):
    print("stash")
    run_command("git stash push")
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

def get_git_branches_as_choice_list():
   # Run the git branch command
    branches = run_command(f'cd {NEATLEAF_DIR}; git branch -a').split('\n')
    choices = []
    for branch in branches:
        sanitized_name =branch.strip().replace('* ', '').replace('+ ', '').replace('remotes/origin/', '')
        choice = Choice(value=sanitized_name, name=sanitized_name)
        choices.append(choice) 
    return choices

def prompt_fzf_git_branches() -> str:
    choices = get_git_branches_as_choice_list()
    # Use inquirer to let the user select a branch
    selected_branch: str = inquirer.fuzzy(message="Select a branch",
                            choices=choices).execute()

    return selected_branch


def main():
    answers = prompt([
        {
            'type': 'list',
            'name': 'action',
            'message': "What do you want to do?",
            'default': 'Add Worktree',
            'choices': ['Add Worktree', 'Checkout Branch']},
            {
            'type': 'list',
            'name': 'directory',
            'message': "Which directory do you want to build?",
            'default': 'dashboard',
            'choices': ['dashboard', 'fleet_management', 'devops', 'other']}])

    branch_name = prompt_fzf_git_branches()
    directory = answers['directory']
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
