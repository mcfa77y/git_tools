import subprocess
from dataclasses import dataclass, field
from typing import List

from InquirerPy.base.control import Choice

from utils import run_command


@dataclass
class WorkTreeJL:
    path: str
    short_path: str = field(init=False)
    commit_hash: str
    name: str
    long_name: str = field(init=False)

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
            self.name = f'(detached) || {self.short_path}'
            self.long_name = f'(detached) || {self.short_path}'
        else:
            self.long_name = f'{self.name} || {self.short_path}'


def format_worktree_names(worktrees: List[WorkTreeJL]):
    # find the longest worktree name
    longest_name_length = max(len(worktree.name) for worktree in worktrees)
    # make all worktree names the same length
    for worktree in worktrees:
        worktree.long_name = worktree.name.ljust(
            longest_name_length) + ' || ' + worktree.short_path


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
        worktrees = list_working_trees(directory)
        format_worktree_names(worktrees)
        # Create choices list
        choices = [
            Choice(value=worktree.path, name=worktree.long_name)
            for worktree in worktrees
        ]

        return choices
    except subprocess.CalledProcessError:
        print("Error: Failed to get git worktrees.")
        return []
