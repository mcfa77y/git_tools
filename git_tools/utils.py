import subprocess
from InquirerPy import inquirer
from logger.logger import Logger

logger = Logger("utils").logger


def run_command(command):
    """Execute a shell command and return its output."""
    logger.debug(f"{command}")
    result = subprocess.check_output(command, shell=True).decode("utf-8").strip()
    # logger.debug(result)
    return result


def prompt_fzf_directory(dir_choices, root_dir, default_choice="") -> str:
    if len(dir_choices) == 1 and dir_choices[0].name == root_dir:
        return ""

    # Use inquirer to let the user select a branch
    directory: str = inquirer.fuzzy(
        message="Select a directory", choices=dir_choices, default=default_choice
    ).execute()

    if directory == root_dir:
        logger.debug("directory == root_dir")
        directory = ""

    return directory
