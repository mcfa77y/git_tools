from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from git_tool_constants import IS_VERBOSE
from utils import run_command


@dataclass
class BranchInfoJL:
    name: str
    date: datetime = field(init=False)
    date_string: str
    author: str
    info: str = field(init=False)
    is_origin: bool = field(init=False)

    def parse(self, string: str):
        """
        Parse the input string to extract date, branch name, and author.

        Parameters:
            string (str): The input string containing date, branch name, and author.

        Returns:
            None
        """
        try:
            parts = string.split()
            self.date_string = parts[0]
            self.name = parts[1]
            self.author = parts[2]
            self.__post_init__()
        except IndexError as e:
            if IS_VERBOSE:
                print(f"[branch_info_jl] {e} - line: {string}")

    def __post_init__(self):
        self.name = self.name.strip()
        self.author = self.author.strip()
        self.date = datetime.strptime(self.date_string, "%Y-%m-%d")
        self.info = f"{self.name} || {self.author} || {self.age}"
        if self.name.startswith("origin/"):
            self.is_origin = True
            self.name = self.name.replace("origin/", "*")
        else:
            self.is_origin = False

    @property
    def age(self) -> str:
        """Age of branch in days"""
        age = (datetime.now() - self.date).days
        return str(age) + " days old"

    @property
    def age_number(self) -> int:
        """Age of branch in days"""
        age = (datetime.now() - self.date).days
        return age

    @property
    def original_name(self) -> str:
        if self.is_origin:
            return self.name.replace("*", "origin/")
        else:
            return self.name


def get_branch_info(directory: str, merged_to_main: bool = False) -> List[BranchInfoJL]:
    """
    Get the branch information for a given directory using git command.

    Parameters:
        directory (str): The directory path to get the branch information from.

    Returns:
        List[BranchInfo]: List of BranchInfo objects containing branch name, last commit date, and author.
    """
    # Get all local and remote branches with their last commit date, branch name, and author
    cmd = [
        f"cd {directory};",
        "git fetch;",
        "git",
        "for-each-ref",
        "--sort=committerdate",
        "--format='%(committerdate:short) %(refname:short) %(authorname)'",
    ]
    if merged_to_main:
        cmd.append("--merged=main")

    output = run_command(" ".join(cmd))
    if output is None:
        return []

    # Parse the output and extract branch information

    branch_info_list: List[BranchInfoJL] = []
    for line in output.splitlines():
        if not line:
            continue
        try:
            branch_info = BranchInfoJL("", "1970-01-01", "")
            branch_info.parse(line)
            branch_info_list.append(branch_info)
        except IndexError:
            continue
    return branch_info_list


def format_branch_info_names(branch_infos: List[BranchInfoJL]):
    """
    Formats the branch information names by making all names the same length and adding the short path.

    Parameters:
        branch_infos (List[BranchInfoJL]): A list of BranchInfoJL objects containing branch information.

    Returns:
        None

    This function finds the longest branch name and author name in the given list of BranchInfoJL objects. It then adjusts the length of all branch names and authors to be the same, ensuring that no name exceeds a maximum length of 40 characters for the name and 30 characters for the author. The function updates the `info` attribute of each BranchInfoJL object with the formatted name, author, and age information.

    Note:
        The function assumes that the `name` attribute of each BranchInfoJL object contains the full branch name, including the "origin/" prefix. The function replaces the "origin/" prefix with an asterisk (*) and truncates the name to the longest_name_length.

    Example:
        >>> branch_infos = [BranchInfoJL(name="origin/feature/branch1", author="John Doe", age="10 days"), BranchInfoJL(name="origin/feature/branch2", author="Jane Smith", age="20 days")]
    """
    # find the longest worktree name
    maximum_branch_name_length = 400
    longest_name_length = max(len(branchInfo.name)
                              for branchInfo in branch_infos)
    longest_name_length = min(longest_name_length, maximum_branch_name_length)

    maximum_author_name_length = 20
    longest_author_length = max(len(branchInfo.author)
                                for branchInfo in branch_infos)
    longest_author_length = min(
        longest_author_length, maximum_author_name_length)

    # make all worktree names the same length
    for branch_info in branch_infos:
        name_short = branch_info.name.replace(
            "origin/", "*")[0:longest_name_length]
        branch_info.name = branch_info.name.removeprefix("origin/")
        branch_info.info = (
            name_short.ljust(longest_name_length)
            + " || "
            + branch_info.author.ljust(longest_author_length)
            + " || "
            + branch_info.age
        )
