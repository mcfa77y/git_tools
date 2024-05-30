import subprocess
from dataclasses import dataclass, field
from typing import List

from InquirerPy.base.control import Choice

from branch_info_jl import BranchInfoJL, get_branch_info
from utils import run_command


@dataclass
class WorkTreeJL:
    path: str
    short_path: str = field(init=False)
    commit_hash: str
    name: str
    long_name: str = field(init=False)
    age_number: int = field(init=False)

    def parse(self, string: str):
        """
        Parse the input string to extract path, commit hash, and name.

        Parameters:
            string (str): The input string containing path, commit hash, and name.

        Returns:
            None
        """
        parts = string.split()
        self.path = parts[0]
        self.commit_hash = parts[1]
        self.name = parts[2]
        self.__post_init__()

    def __post_init__(self):
        self.path = self.path.strip()
        self.short_path = self.path.replace("/Users/joe/Projects/nl-worktrees",
                                            "")

        self.name = self.name.strip().replace('[', '').replace(']', '')
        if "(detached" in self.name:
            self.name = self.short_path
            self.long_name = self.short_path

        if self.name in self.short_path:
            self.long_name = self.name
        else:
            self.long_name = f'{self.name} || {self.short_path}'
        self.age_number = 0

    def update_name(self, branch_info: BranchInfoJL):
        self.long_name = branch_info.age + ' || ' + self.long_name
        self.age_number = branch_info.age_number


def format_worktree_names(worktrees: List[WorkTreeJL]):
    """
    A function to format worktree names by making all names the same length and adding the short path.

    Parameters:
        worktrees (List[WorkTreeJL]): A list of WorkTreeJL objects representing different worktrees.

    Returns:
        None
    """
    # find the longest worktree name
    longest_name_length = max(len(worktree.long_name) for worktree in worktrees)
    # make all worktree names the same length
    for worktree in worktrees:
        worktree.long_name = worktree.long_name.ljust(
            longest_name_length)
    # Sort worktrees by age_number
    worktrees.sort(key=lambda worktree: worktree.age_number)


def list_working_trees(directory) -> List[WorkTreeJL]:
    """Return a list of working trees."""
    output = run_command(f'cd {directory} && git worktree list')

    worktrees_jl = []
    for line in output.splitlines():
        worktree = WorkTreeJL(path='', commit_hash='', name='')
        worktree.parse(line)
        worktrees_jl.append(worktree)
    # Sort worktrees by long_name
    worktrees_jl.sort(key=lambda worktree: worktree.long_name)

    return worktrees_jl


def create_choices_for_worktrees(directory):
    """Get a list of current git working trees."""
    try:
        branch_info = get_branch_info(directory, merged_to_main=False)

        branch_name_to_branch_info = {}
        for branch_info_jl in branch_info:
            branch_name_to_branch_info[branch_info_jl.name] = branch_info_jl

        worktrees = list_working_trees(directory)
        for worktree in worktrees:
            if worktree.name in branch_name_to_branch_info:
                worktree.update_name(branch_name_to_branch_info[
                    worktree.name])
            else:
                print(f'[worktree_jl] No branch info for {worktree}')
        format_worktree_names(worktrees)

        # Create choices list
        choices = [
            Choice(value=worktree.path, name=worktree.long_name)
            for worktree in worktrees
        ]
        return choices
    except subprocess.CalledProcessError:
        print("[worktree_jl] Error: Failed to get git worktrees.")
        return []
