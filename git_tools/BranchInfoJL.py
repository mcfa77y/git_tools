from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from utils import run_command


@dataclass
class BranchInfoJL:
    name: str
    date: datetime = field(init=False)
    date_string: str
    author: str

    def __post_init__(self):
        self.name = self.name.strip()
        self.author = self.author.strip()
        self.date = datetime.strptime(self.date_string, '%Y-%m-%d')

    @property
    def age(self) -> int:
        """Age of branch in days"""
        return (datetime.now() - self.date).days


def get_branch_info(directory: str) -> List[BranchInfoJL]:
    """
    Get the branch information for a given directory using git command.

    Parameters:
        directory (str): The directory path to get the branch information from.

    Returns:
        List[BranchInfo]: List of BranchInfo objects containing branch name, last commit date, and author.
    """
    # Get all local and remote branches with their last commit date, branch name, and author
    cmd = [
        f"cd {directory} &&",
        "git",
        "for-each-ref",
        "--sort=committerdate",
        "--merged",
        "main",
        "--format='%(committerdate:short) %(refname:short) %(authorname)'",
    ]
    output = run_command(" ".join(cmd))
    if output is None:
        return []

    # Parse the output and extract branch information

    branch_info_list: List[BranchInfoJL] = []
    for line in output.splitlines():
        if not line:
            continue
        try:
            date_str, branch_name, author = line.split(None, 2)
            branch_info = BranchInfoJL(name=branch_name, date_string=date_str, author=author)
            branch_info_list.append(branch_info)
            # print(f'Parsed: {branch_info.age} days | {branch_info.author} | {branch_info.name} ')
        except ValueError as e:
            print(f"Error parsing line: {line}")
            print(f'\tError: {str(e)}')
    return branch_info_list