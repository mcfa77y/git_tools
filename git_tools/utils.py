import subprocess

from InquirerPy import inquirer

from constants import DEBUG, DIR_CHOICES


def run_command(command):
    """Execute a shell command and return its output."""
    if DEBUG:
        print(f'{command}')
    return subprocess.check_output(command, shell=True).decode('utf-8').strip()


def prompt_fzf_directory(default_choice="") -> str:
    # Use inquirer to let the user select a branch
    directory: str = inquirer.fuzzy(message="Select a branch",
                                    choices=DIR_CHOICES,
                                    default=default_choice
                                    ).execute()

    return directory
