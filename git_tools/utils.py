import subprocess
from typing import List

from InquirerPy import inquirer

from logger.logger import Logger, LogLevel

logger = Logger("utils", LogLevel.WARNING).logger_jl


def run_commands(commands: list[str]):
    for command in commands:
        run_command(command)


def run_command(command: str):
    """Execute a shell command and return its output."""
    logger.debug(f"{command}")
    logger.debug(f"Running command: {command}")

    # Use bash explicitly to ensure command substitution works
    result = (
        subprocess.check_output(["bash", "-c", command], stderr=subprocess.STDOUT)
        .decode("utf-8")
        .strip()
    )

    if command.strip().startswith("echo"):
        print(result)

    logger.debug(f"Command output: {result}")
    return result


def prompt_fzf_directory(dir_choices, root_dir, default_choice="") -> str:
    logger.debug(f"dir_choices: {dir_choices}")
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
