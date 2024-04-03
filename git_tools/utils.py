import subprocess
from typing import List
from InquirerPy.base.control import Choice
from WorktreeJL import WorkTreeJL


def run_command(command):
    """Execute a shell command and return its output."""
    return subprocess.check_output(command, shell=True).decode('utf-8').strip()


def list_working_trees(directory) -> List[WorkTreeJL]:
    """Return a list of working trees."""
    output = run_command(f'cd {directory} && git worktree list')
    
    worktrees_jl = []
    for line in output.splitlines():
        parts = line.split()
        path = parts[0]
        commit_hash = parts[1]
        short_path = path.replace("/Users/joe/Projects/nl-worktrees", "")
        name = f'{parts[2]} - path: {short_path}'
        if "(detached" in parts[2]:
            name = f'(detached) {short_path}'
        worktree = WorkTreeJL(path=path,
                              commit_hash=commit_hash,
                              name=name)
        worktrees_jl.append(worktree)
    # Sort worktrees by name
    worktrees_jl.sort(key=lambda worktree: worktree.name)

    return worktrees_jl


def create_choices_for_worktrees(directory):
    """Get a list of current git working trees."""
    try:
        worktrees = list_working_trees(directory)

        # Create choices list
        choices = [
            Choice(value=worktree.path, name=worktree.name)
            for worktree in worktrees
        ]

        return choices
    except subprocess.CalledProcessError:
        print("Error: Failed to get git worktrees.")
        return []
