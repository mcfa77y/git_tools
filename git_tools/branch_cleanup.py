# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "alive-progress",
#     "click",
#     "loguru",
#     "inquirerpy",
# ]
# ///
import concurrent.futures
import subprocess
from datetime import datetime, timedelta
from typing import List, Set

import click
from alive_progress import alive_bar
from InquirerPy import inquirer

from branch_info_jl import BranchInfoJL, format_branch_info_names, get_branch_info


def run_git_command(
    cmd: List[str], directory: str, swallow_output: bool = False
) -> str:
    """Run a git command in the specified directory.

    Args:
        cmd (List[str]): The command to run as a list of strings.
        directory (str): The directory where the command should be run.
        swallow_output (bool, optional): Whether to suppress the command output. Defaults to False.

    Returns:
        str: The output of the command as a string, or an empty string if swallow_output is True.
    """
    try:
        if swallow_output:
            result = subprocess.run(
                cmd,
                cwd=directory,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,  # Suppress stderr for expected failures
                check=False,  # Don't raise exception on non-zero exit
                text=True,
            )
            return ""

        result = subprocess.check_output(cmd, text=True, cwd=directory)
        return result.strip()
    except subprocess.CalledProcessError as e:
        import traceback
        click.echo(f"Command failed with error code {e.returncode}")
        click.echo(f"Stack trace: {traceback.format_exc()}")
        return ""


def get_merged_branches(directory: str) -> List[str]:
    """Get list of branches that have been merged into main/master."""
    try:
        # Get the main branch name
        main_branch = get_main_branch_name(directory)
        if not main_branch:
            return []
        
        # Get merged branches
        result = run_git_command(
            ["git", "branch", "--merged", main_branch], directory
        )
        if not result:
            return []
        
        branches = []
        for line in result.split('\n'):
            branch = line.strip().replace('* ', '')
            if branch and branch != main_branch:
                branches.append(branch)
        
        return branches
    except Exception as e:
        click.echo(f"Error getting merged branches: {e}")
        return []


def get_main_branch_name(directory: str) -> str:
    """Get the main branch name (main, master, or develop)."""
    common_main_branches = ["main", "master", "develop"]
    
    for branch in common_main_branches:
        try:
            result = run_git_command(
                ["git", "rev-parse", "--verify", branch], directory, swallow_output=True
            )
            if result is not None:  # Branch exists
                return branch
        except subprocess.CalledProcessError:
            continue
    
    # If none of the common names exist, try to get the default branch
    try:
        result = run_git_command(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"], directory
        )
        if result:
            return result.replace('refs/remotes/origin/', '')
    except subprocess.CalledProcessError:
        pass
    
    return ""


def get_stale_branches(directory: str, threshold_days: int) -> List[BranchInfoJL]:
    """Get branches that haven't been committed to in threshold_days."""
    try:
        branch_info_list = get_branch_info(directory, merged_to_main=False)
        
        # Ensure we have a list (handle case where get_branch_info might fail)
        if not isinstance(branch_info_list, list):
            click.echo(f"Error: Expected list from get_branch_info, got {type(branch_info_list)}")
            return []
        
        # Filter branches based on age
        stale_branches = [
            branch_info for branch_info in branch_info_list
            if hasattr(branch_info, 'age_number') and 
               hasattr(branch_info, 'is_origin') and
               branch_info.age_number >= threshold_days and 
               not branch_info.is_origin
        ]
        
        # Filter out protected branches
        stale_branches = [
            branch for branch in stale_branches
            if hasattr(branch, 'name') and filter_by_branch_name(branch.name)
        ]
        
        return sorted(stale_branches, key=lambda x: getattr(x, 'age', ''), reverse=True)
    except Exception as e:
        import traceback
        click.echo(f"Error getting stale branches: {e}")
        click.echo(f"Stack trace: {traceback.format_exc()}")
        return []


def filter_by_branch_name(branch_name: str) -> bool:
    """Filter out protected branches that should not be deleted."""
    # Ensure branch_name is a string
    click.echo(f"filter_by_branch_name: 00 {branch_name}")
    if not isinstance(branch_name, str):
        return False
    
    click.echo(f"filter_by_branch_name: 01 {branch_name}")
    exclude_branch_list = ["main", "master", "develop", "release", "prod", "tag/"]
    click.echo(f"filter_by_branch_name: 02 {branch_name}")
    
    # Expand the all() generator expression to avoid Click parsing issues
    for ignore_branch in exclude_branch_list:
        if ignore_branch in branch_name:
            click.echo(f"filter_by_branch_name: 03 {branch_name}")
            return False
    click.echo(f"filter_by_branch_name: 04 {branch_name}")
    return True


def get_squashed_branches(directory: str) -> List[str]:
    """Get branches that have been squashed and merged."""
    try:
        all_branches = _get_all_local_branches(directory)
        main_branch = get_main_branch_name(directory)
        
        if not main_branch:
            return []
        
        return _find_squashed_branches(directory, all_branches, main_branch)
        
    except Exception as e:
        click.echo(f"Error getting squashed branches: {e}")
        return []


def _get_all_local_branches(directory: str) -> List[str]:
    """Get list of all local branch names."""
    result = run_git_command(["git", "branch", "-a"], directory)
    if not result:
        return []
    
    branches = []
    for line in result.split('\n'):
        branch = line.strip().replace('* ', '').replace('remotes/origin/', '')
        if branch and 'HEAD' not in branch:
            branches.append(branch)
    
    return branches


def _find_squashed_branches(directory: str, all_branches: List[str], main_branch: str) -> List[str]:
    """Identify branches that appear to be squashed and merged."""
    squashed_branches = []
    
    for branch in all_branches:
        if not _should_check_branch(branch, main_branch):
            continue
            
        if _is_branch_squashed(directory, branch, main_branch):
            squashed_branches.append(branch)
    
    return squashed_branches


def _should_check_branch(branch: str, main_branch: str) -> bool:
    """Determine if a branch should be checked for squashing."""
    return branch != main_branch and filter_by_branch_name(branch)


def _is_branch_squashed(directory: str, branch: str, main_branch: str) -> bool:
    """Check if a branch appears to be squashed into main."""
    try:
        merge_base = run_git_command(
            ["git", "merge-base", main_branch, branch], directory
        )
        
        if not merge_base:
            return False
            
        branch_commits = run_git_command(
            ["git", "log", "--oneline", f"{merge_base}..{branch}"], directory
        )
        
        if not branch_commits:
            return False
            
        # Simple heuristic: if branch has commits but they're not individually in main,
        # it might be squashed
        main_commits = run_git_command(
            ["git", "log", "--oneline", main_branch], directory
        )
        
        return bool(main_commits and branch_commits)
        
    except subprocess.CalledProcessError:
        return False


def select_branches_interactive(branch_info_list: List[BranchInfoJL], 
                               branch_names: List[str] = None) -> List[str]:
    """Interactively select branches to delete."""
    if branch_names:
        # Simple selection for string lists
        selected = inquirer.fuzzy(
            message="Select branches to delete:",
            choices=branch_names,
            multiselect=True,
            default="joe/rhl-2",
        ).execute()
        return selected
    else:
        # Selection for BranchInfoJL objects
        format_branch_info_names(branch_info_list)
        branch_choices = [
            {"name": branch_info.info, "value": branch_info.name}
            for branch_info in branch_info_list
        ]
        
        selected = inquirer.fuzzy(
            message="Select branches to delete:",
            choices=branch_choices,
            multiselect=True,
        ).execute()
        return selected


def delete_branches_concurrently(directory: str, branches: List[str]) -> None:
    """Delete multiple branches concurrently with progress bar."""
    if not branches:
        click.echo("No branches to delete.")
        return
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(delete_single_branch, branch, directory) 
            for branch in branches
        ]
        
        with alive_bar(len(futures), title="Deleting branches") as progress_bar:
            deleted_count = 0
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        deleted_count += 1
                    progress_bar()
                except Exception as e:
                    click.echo(f"Error deleting branch: {e}")
                    progress_bar()
    
    click.echo(f"Successfully deleted {deleted_count}/{len(branches)} branches.")


def delete_single_branch(branch_name: str, directory: str) -> bool:
    """Delete a single local branch."""
    try:
        # First, try to delete the local branch
        run_git_command(
            ["git", "branch", "-D", branch_name], directory, swallow_output=True
        )
        
       
        # Also try to delete the remote tracking branch if it exists
        run_git_command(
            ["git", "branch", "-dr", f"origin/{branch_name}"], 
            directory, 
            swallow_output=True
        )
        
        return True
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to delete branch '{branch_name}': {e}")
        return False


@click.group()
def cleanup():
    """Git branch cleanup utilities."""
    pass


@cleanup.command()
@click.option(
    "--threshold_days",
    default=30,
    type=int,
    help="Delete branches older than threshold days (default: 30)."
)
@click.option(
    "--directory", 
    default=".", 
    help="Directory to execute the git command in"
)
@click.option(
    "--auto", 
    is_flag=True, 
    help="Automatically delete all stale branches without confirmation"
)
def stale(threshold_days, directory, auto):
    """Clean up stale branches based on last commit date."""
    click.echo(f"Finding stale branches older than {threshold_days} days...")
    
    stale_branches = get_stale_branches(directory, threshold_days)
    
    if not stale_branches:
        click.echo("No stale branches found.")
        return
    
    click.echo(f"Found {len(stale_branches)} stale branches:")
    for branch in stale_branches[:10]:  # Show first 10
        click.echo(f"  - {branch.info}")
    if len(stale_branches) > 10:
        click.echo(f"  ... and {len(stale_branches) - 10} more")
    
    if auto:
        branches_to_delete = [branch.name for branch in stale_branches]
    else:
        branches_to_delete = select_branches_interactive(stale_branches)
    
    if branches_to_delete:
        delete_branches_concurrently(directory, branches_to_delete)


@cleanup.command()
@click.option(
    "--directory", 
    default=".", 
    help="Directory to execute the git command in"
)
@click.option(
    "--auto", 
    is_flag=True, 
    help="Automatically delete all merged branches without confirmation"
)
def merged(directory, auto):
    """Clean up branches that have been merged to main."""
    click.echo("Finding merged branches...")
    
    merged_branches = get_merged_branches(directory)
    
    if not merged_branches:
        click.echo("No merged branches found.")
        return
    
    click.echo(f"Found {len(merged_branches)} merged branches:")
    for branch in merged_branches:
        click.echo(f"  - {branch}")
    
    if auto:
        branches_to_delete = merged_branches
    else:
        branches_to_delete = select_branches_interactive([], merged_branches)
    
    if branches_to_delete:
        delete_branches_concurrently(directory, branches_to_delete)


@cleanup.command()
@click.option(
    "--directory", 
    default=".", 
    help="Directory to execute the git command in"
)
@click.option(
    "--auto", 
    is_flag=True, 
    help="Automatically delete all squashed branches without confirmation"
)
def squashed(directory, auto):
    """Clean up branches that have been squashed and merged."""
    click.echo("Finding squashed branches...")
    
    squashed_branches = get_squashed_branches(directory)
    
    if not squashed_branches:
        click.echo("No squashed branches found.")
        return
    
    click.echo(f"Found {len(squashed_branches)} potentially squashed branches:")
    for branch in squashed_branches:
        click.echo(f"  - {branch}")
    
    if auto:
        branches_to_delete = squashed_branches
    else:
        branches_to_delete = select_branches_interactive([], squashed_branches)
    
    if branches_to_delete:
        delete_branches_concurrently(directory, branches_to_delete)


@cleanup.command()
@click.option(
    "--threshold_days",
    default=30,
    type=int,
    help="Include branches older than threshold days (default: 30)."
)
@click.option(
    "--directory", 
    default=".", 
    help="Directory to execute the git command in"
)
@click.option(
    "--auto", 
    is_flag=True, 
    help="Automatically delete all cleanup candidates without confirmation"
)
def all(threshold_days, directory, auto):
    """Clean up all types of branches (stale, merged, and squashed)."""
    click.echo("Finding all branches that can be cleaned up...")
    
    # Get all types of branches
    stale_branches = get_stale_branches(directory, threshold_days)
    merged_branches = get_merged_branches(directory)
    squashed_branches = get_squashed_branches(directory)
    
    # Combine and deduplicate
    all_branches = set()
    all_branches.update(branch.name for branch in stale_branches)
    all_branches.update(merged_branches)
    all_branches.update(squashed_branches)
    
    if not all_branches:
        click.echo("No branches found for cleanup.")
        return
    
    click.echo(f"Found {len(all_branches)} branches for cleanup:")
    for branch in sorted(all_branches):
        click.echo(f"  - {branch}")
    
    if auto:
        branches_to_delete = list(all_branches)
    else:
        branches_to_delete = select_branches_interactive([], list(all_branches))
    
    if branches_to_delete:
        delete_branches_concurrently(directory, branches_to_delete)


@cleanup.command()
@click.option(
    "--directory", 
    default=".", 
    help="Directory to execute the git command in"
)
def custom(directory):
    """Interactively select and delete any local branches."""
    click.echo("Getting all local branches...")
    
    try:
        # Get all local branches
        result = run_git_command(["git", "branch"], directory)
        if not result:
            click.echo("No local branches found.")
            return
        
        # Parse branch names
        all_branches = []
        for line in result.split('\n'):
            branch = line.strip().replace('* ', '')
            click.echo(f"Branch: {branch}")
            # Only add if branch is a non-empty string and passes filter
            if isinstance(branch, str) and branch and filter_by_branch_name(branch):
                all_branches.append(branch)
        all_branches.sort()
        if not all_branches:
            click.echo("No deletable local branches found (protected branches excluded).")
            return
        
        click.echo(f"Found {len(all_branches)} local branches:")
        for branch in sorted(all_branches):
            click.echo(f"  - {branch}")
        
        # Interactive selection
        branches_to_delete = select_branches_interactive([], all_branches)
        
        if branches_to_delete:
            click.echo(f"\nSelected {len(branches_to_delete)} branches for deletion:")
            for branch in branches_to_delete:
                click.echo(f"  - {branch}")
            
            confirm = inquirer.confirm(
                "Are you sure you want to delete these branches?",
                default=False
            ).execute()
            
            if confirm:
                delete_branches_concurrently(directory, branches_to_delete)
            else:
                click.echo("Deletion cancelled.")
        else:
            click.echo("No branches selected for deletion.")
            
    except Exception as e:
        import traceback
        click.echo(f"Error getting branches: {e}")
        click.echo(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    cleanup()
