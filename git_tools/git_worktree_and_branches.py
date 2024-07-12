import os

import click
from InquirerPy import inquirer, prompt
from InquirerPy.base.control import Choice

from branch_info_jl import format_branch_info_names, get_branch_info
from constants import NEATLEAF_DIR, WORKTREE_DIR
from utils import prompt_fzf_directory, run_command


def common_checkout_branch(branch_name, directory, here_directory):
    print(f"stash {here_directory}")
    run_command(f"cd {here_directory}; git stash push")
    print(f"switch {branch_name}")
    run_command(f"git switch {branch_name}")
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
    new_branch_name = branch_name.replace('*', '')
    new_worktree_dir = f"{WORKTREE_DIR}/{new_branch_name}"
    print(f"[worktree add] git worktree add {new_worktree_dir}")

    run_command(f"git worktree add {new_worktree_dir} {new_branch_name}")
    os.chdir(f"{new_worktree_dir}")
    copy_husky_dir()
    print("[worktree add] copy envs")
    run_command(f"cp {NEATLEAF_DIR}/dashboard/.env dashboard")
    os.chdir(directory)
    run_command("code .")
    # check if there is a .yarn lock file, if so run yarn
    if os.path.exists(".yarn.lock"):
        print("[worktree add] yarn")
        run_command("yarn")
    run_command("cd $HERE")


def update_version(version_string, update_type):
    old_version = version_string.split('-')[-1]
    components = old_version.split('.')
    if update_type == 'major':
        components[1] = '0'
        components[2] = '0'
        components[0] = str(int(components[0]) + 1)
    elif update_type == 'minor':
        components[2] = '0'
        components[1] = str(int(components[1]) + 1)
    elif update_type == 'patch':
        components[2] = str(int(components[2]) + 1)
    print(f'components: {components}')
    new_version = '.'.join(components)
    new_version = f'{version_string.split("-")[0]}-{new_version}'
    return new_version.split('/')[1]


def release_process():
    # choose a prod branch for which to create a release
    tag_name = prompt_fzf_git_branches('release/')
    print(f"release branch: {tag_name}")
    # prompt user for version type major, minor, patchj
    version_type = inquirer.fuzzy(
        message="What version type do you want to release?",
        choices=['major', 'minor', 'patch'],
        default='minor'
    ).execute()
    print(f'version type: {version_type}')

    updated_version = update_version(tag_name, version_type)
    print(f'new version: {updated_version}')
    new_tag = f'tag/{updated_version}'
    print(f'new tag: {new_tag}')
    new_release_branch = f'release/{updated_version}'
    print(f'new release branch: {new_release_branch}')

    # get the latest tag
    os.chdir(NEATLEAF_DIR)
    # stash current changes with message 'pre-release changes'
    run_command(
        f"git stash push -m 'pre-release changes {new_release_branch}'")
    #  switch main
    run_command("git switch main")
    # pull latest changes
    run_command("git pull")
    # create a new release branch
    run_command(f"git checkout -b {new_release_branch}")
    # switch to the new release branch
    run_command(f"git switch {new_release_branch}")
    #  push branch to origin
    run_command(f"git push origin {new_release_branch} --no-verify")
    # add the new tag
    run_command(
        f"git tag --annotate --force {new_tag} --message 'creating {new_tag}'")
    # push the new tag
    run_command(f"git push origin {new_tag} --no-verify")
    # switch back to the main branch
    run_command("git switch main")


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


def prompt_fzf_git_branches(branch_name: str = "") -> str:
    choices = get_branches_as_choice_list()
    # Use inquirer to let the user select a branch
    selected_branch: str = inquirer.fuzzy(message="Select a branch",
                                          default=branch_name,
                                          choices=choices).execute()

    return selected_branch


ADD_WORKTREE = "Add Worktree"
CHECKOUT_BRANCH = "Checkout Branch"
RELEASE_PROCESS = "Release Process"
ACTIONS = [ADD_WORKTREE, CHECKOUT_BRANCH, RELEASE_PROCESS]


@click.command()
@click.option(
    '--action',
    default='',
    help='What do you want to do?',
)
@click.option('--directory',
              default='',
              help='Directory to execute the git command in')
@click.option('--here_directory',
              default='',
              help='Directory to execute the git command in')
def main(action, directory, here_directory):
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

    if answers['action'] == CHECKOUT_BRANCH:
        branch_name = prompt_fzf_git_branches()
        if directory == '':
            directory = prompt_fzf_directory()
        common_checkout_branch(branch_name, directory, here_directory)
    elif answers['action'] == ADD_WORKTREE:
        branch_name = prompt_fzf_git_branches()
        if directory == '':
            directory = prompt_fzf_directory()
        common_worktree_add(branch_name, directory)
    elif answers['action'] == RELEASE_PROCESS:
        release_process()


if __name__ == "__main__":
    print(f"[worktree add] fetch {NEATLEAF_DIR}")
    os.chdir(NEATLEAF_DIR)
    run_command("git fetch --prune")
    main()
