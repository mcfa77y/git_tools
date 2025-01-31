import subprocess

from InquirerPy import inquirer


def run_command(command, is_verbose=False):
    """Execute a shell command and return its output."""
    if is_verbose:
        print(f"{command}")
    return subprocess.check_output(command, shell=True).decode("utf-8").strip()


def prompt_fzf_directory(dir_choices, root_dir, default_choice="") -> str:
    # Use inquirer to let the user select a branch
    directory: str = inquirer.fuzzy(
        message="Select a directory", choices=dir_choices, default=default_choice
    ).execute()

    if directory == root_dir:
        directory = ''

    return directory
