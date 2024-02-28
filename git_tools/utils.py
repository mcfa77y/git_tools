import subprocess
from typing import List


def run_command(command):
    """Execute a shell command and return its output."""
    return subprocess.check_output(command, shell=True).decode('utf-8').strip()


def list_working_trees(directory) -> List[str]:
    """Return a list of working trees."""
    output = run_command(f'cd {directory} && git worktree list')
    worktrees = [line.split()[0] for line in output.splitlines()]
    worktrees.sort(key=lambda worktree: worktree.split('/')[-1].lower(),
                   reverse=True)
    return worktrees
