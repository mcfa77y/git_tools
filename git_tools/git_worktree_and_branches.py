# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "InquirerPy"
# ]
# ///
import os

import click
from InquirerPy import inquirer, prompt
from InquirerPy.base.control import Choice

from branch_info_jl import format_branch_info_names, get_branch_info
from git_tool_constants import (BUILD_FN, DIR_CHOICES, GIT_DIR, ROOT_DIR,
                                WORKTREE_DIR)
from utils import prompt_fzf_directory, run_command


def common_checkout_branch(branch_name, directory, here_directory):
    print(f"stash {here_directory}")
    run_command(f"cd {here_directory}; git stash push")
    print(f"switch {branch_name}")
    run_command(f"git switch {branch_name}")
    print("stash pop")
    run_command("git stash pop")
    BUILD_FN(directory, git_dir=GIT_DIR)


def common_worktree_add(branch_name, directory):
    new_branch_name = branch_name.replace("*", "")
    new_worktree_dir = f"{WORKTREE_DIR}/{new_branch_name}"
    print(f"[worktree add] git worktree add {new_worktree_dir}")
    if os.path.exists(new_worktree_dir):
        print("[worktree add] worktree already exists")
        BUILD_FN(new_worktree_dir, git_dir=GIT_DIR)
        return
    try:
        run_command(f"git worktree add {new_worktree_dir} {new_branch_name}")
    except Exception as e:
        print(f"[worktree add] Exception while running git worktree add {e}")

    if "root" in directory:
        BUILD_FN(directory, git_dir=GIT_DIR)
    else:
        BUILD_FN(new_worktree_dir, git_dir=GIT_DIR)


def update_version(version_string, update_type):
    old_version = version_string.split("-")[-1]
    components = old_version.split(".")
    if update_type == "major":
        components[1] = "0"
        components[2] = "0"
        components[0] = str(int(components[0]) + 1)
    elif update_type == "minor":
        components[2] = "0"
        components[1] = str(int(components[1]) + 1)
    elif update_type == "patch":
        components[2] = str(int(components[2]) + 1)
    print(f"components: {components}")
    new_version = ".".join(components)
    new_version = f"{version_string.split('-')[0]}-{new_version}"
    return new_version.split("/")[1]


def release_process():
    # choose a prod branch for which to create a release
    tag_name = prompt_fzf_git_branches("release/")
    print(f"release branch: {tag_name}")
    # prompt user for version type major, minor, patchj
    version_type = inquirer.fuzzy(
        message="What version type do you want to release?",
        choices=["major", "minor", "patch"],
        default="minor",
    ).execute()
    print(f"version type: {version_type}")

    updated_version = update_version(tag_name, version_type)
    print(f"new version: {updated_version}")
    new_tag = f"tag/{updated_version}"
    print(f"new tag: {new_tag}")
    new_release_branch = f"release/{updated_version}"
    print(f"new release branch: {new_release_branch}")

    # get the latest tag
    os.chdir(GIT_DIR)
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
    branches = get_branch_info(GIT_DIR)
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
    selected_branch: str = inquirer.fuzzy(
        message="Select a branch", default=branch_name, choices=choices
    ).execute()

    return selected_branch


ADD_WORKTREE = "Add Worktree"
CHECKOUT_BRANCH = "Checkout Branch"
RELEASE_PROCESS = "Release Process"
INTERACTIVE = "Interactive"
ACTIONS = [ADD_WORKTREE, CHECKOUT_BRANCH, RELEASE_PROCESS, INTERACTIVE]


@click.command()
@click.option(
    "--action",
    type=click.Choice(ACTIONS),
    default=INTERACTIVE,
    help="What do you want to do?",
)
@click.option(
    "--branch_name",
    default="",
    help="Branch name to checkout",
)
@click.option("--directory", default="", help="Directory to execute the git command in")
@click.option(
    "--here_directory", default="", help="Directory to execute the git command in"
)
def main(action, directory, here_directory, branch_name):
    if action == INTERACTIVE:
        answers = prompt(
            [
                {
                    "type": "list",
                    "name": "action",
                    "message": "What do you want to do?",
                    "default": ADD_WORKTREE,
                    "choices": ACTIONS,
                }
            ]
        )
    else:
        answers = {"action": action}
    if answers["action"] == CHECKOUT_BRANCH:
        branch_name = prompt_fzf_git_branches(branch_name=branch_name)
        if directory == "":
            directory = prompt_fzf_directory(
                dir_choices=DIR_CHOICES, root_dir=ROOT_DIR)
        common_checkout_branch(branch_name, directory, here_directory)
    elif answers["action"] == ADD_WORKTREE:
        branch_name = prompt_fzf_git_branches(branch_name=branch_name)
        if directory == "":
            directory = prompt_fzf_directory(
                dir_choices=DIR_CHOICES, root_dir=ROOT_DIR)
        common_worktree_add(branch_name, directory)
    elif answers["action"] == RELEASE_PROCESS:
        release_process()


if __name__ == "__main__":
    print(f"[worktree add] fetch {GIT_DIR}")
    os.chdir(GIT_DIR)
    run_command("git fetch --prune")
    main()
