import concurrent.futures
import subprocess
from typing import List

import click
import pretty_errors
from alive_progress import alive_bar
from InquirerPy import inquirer

from BranchInfoJL import BranchInfoJL, get_branch_info


def run_git_command(cmd: List[str],
                    directory: str,
                    swollow_output: bool = False) -> str:
    """Run a git command in the specified directory.

    Args:
        cmd (List[str]): The command to run as a list of strings.
        directory (str): The directory where the command should be run.
        swollow_output (bool, optional): Whether to suppress the command output. Defaults to False.

    Returns:
        str: The output of the command as a string, or an empty string if swollow_output is True.
    """
    try:
        print(f'Running command: {" ".join(cmd)}')
        if swollow_output:
            result = subprocess.run(cmd,
                                    cwd=directory,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE,
                                    check=True,
                                    text=True)
            return ''

        result = subprocess.check_output(cmd, text=True, cwd=directory)
        return result.strip()
    except subprocess.CalledProcessError as e:
        click.echo(f"Command failed with error code {e.returncode}")
        return None


@click.command()
@click.option(
    '--threshold_days',
    default=30,
    type=int,
    help='Filter branches that are older than threshold days. default 30 days.')
@click.option('--directory',
              default='.',
              help='Directory to execute the git command in')
def get_stale_branches(threshold_days, directory):
    """
    Return branches that were last updated more than the given threshold ago.

    Parameters:
    - threshold (int): Time threshold in days.
    - directory (str): Directory to execute the git command in
    """

    # Fetch the latest data about all remote branches
    run_git_command(["git", "fetch"], directory)

    # Filter branches based on the threshold date, calculate their age, and get the author
    branch_info_list = get_branch_info(directory, merged_to_main=True)
    branch_info_filtered_list: List[BranchInfoJL] = branch_info_list.copy()
    # Filter branches based on their age
    branch_info_filtered_list = list(
        filter(lambda branch_info: branch_info.age_number >= threshold_days,
               branch_info_filtered_list))
    # Filter branches based on their name
    branch_info_filtered_list = list(
        filter(lambda branch_info: filter_by_branch_name(branch_info.name),
               branch_info_filtered_list))

    # Sort the branches from oldest to youngest
    sorted_branches = sorted(branch_info_filtered_list,
                             key=lambda branch_info: branch_info.age,
                             reverse=True)

    # Print message if there are no branches
    if not sorted_branches:
        print("No branches found.")
        return

    delete_branches(directory, sorted_branches)


def filter_by_branch_name(branch_name: str) -> bool:
    """
    Filter branches based on their name if they include "main", "release", "prod", or "tag/" then exclude them.

    Parameters:
    - branch_name (str): The name of the branch to filter.

    Returns:
    - bool: True if the branch name does not include any of the excluded branch names, False otherwise.
    """
    # Filter branches based on their name if they include "main", "release", "prod", or "tag/" then exclude them
    exclude_branch_list = ['main', 'release', 'prod', 'tag/']
    return all(ignore_branch not in branch_name
               for ignore_branch in exclude_branch_list)


def select_branches(branch_info_list: List[BranchInfoJL]):
    """
    A function to select branches based on author information.

    Parameters:
    branch_info_list (List[BranchInfoJL]): A list of BranchInfoJL objects containing branch information.

    Returns:
    List[str]: A list of selected branch names.
    """
    authors = sorted(set(
        branch_info.author for branch_info in branch_info_list))
    selected_authors = inquirer.fuzzy(message='Select authors:',
                                      choices=list(authors),
                                      multiselect=True,
                                      default='joe').execute()

    branch_choices = [{
        'name':
            f"(Age: {branch_info.age} days, {branch_info.name}, Author: {branch_info.author})",
        'value':
            branch_info.name
    }
                      for branch_info in branch_info_list
                      if branch_info.author in selected_authors]

    selected_branches = inquirer.fuzzy(message='Select branches:',
                                       choices=branch_choices,
                                       multiselect=True).execute()

    return selected_branches


def delete_branches_concurrenlty(directory, branches):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(delete_branch, branch, directory)
            for branch in branches
        ]
        with alive_bar(len(futures)) as progress_bar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                    progress_bar()
                except Exception as e:
                    print(f"An error occurred during branch deletion: {str(e)}")


def delete_branch(branch, directory):
    # Check if the branch is a local branch
    if branch.startswith("origin/"):
        # Delete the remote branch
        new_branch_name = branch.replace("origin/", "")
        run_git_command([
            "git", "push", "origin", "--delete", "--no-verify", new_branch_name
        ],
                        directory,
                        swollow_output=True)
    else:
        # Delete the local branch
        run_git_command(["git", "branch", "-D", branch], directory)


def delete_branches(directory: str, branch_info_list: List[BranchInfoJL]):
    branches = select_branches(branch_info_list)
    delete_branches_concurrenlty(directory, branches)


if __name__ == '__main__':
    get_stale_branches()
