import os

from utils import run_command
from logger.logger import Logger

logger = Logger("build_fn").logger


def default_build_function(directory: str):
    # Change to the selected directory
    print(os.getcwd())
    os.chdir(directory)
    run_command("code .")
    # only run next command if there is a yarn.lock file present
    if os.path.exists("yarn.lock"):
        run_command("yarn")
        return
    if os.path.exists("pnpm-lock.yaml"):
        run_command("pnpm install")
        return
    if os.path.exists("package-lock.json"):
        run_command("npm install")
        return
    if os.path.exists("bun.lock") or os.path.exists("bun.lockb"):
        run_command("bun install")
        return


def copy_husky_dir(git_dir: str):
    os.makedirs(".husky/_", exist_ok=True)
    print("[build_fn] copy husky dir")
    run_command(f"cp {git_dir}/.husky/_/husky.sh .husky/_/")
    # print("[worktree add] create .git dir")
    # os.makedirs(".git", exist_ok=True)


def neatleaf_build(directory: str, git_dir: str):
    copy_husky_dir(git_dir)
    print("[build_fn] copy envs")
    run_command(f"cp {git_dir}/dashboard/.env dashboard")
    default_build_function(directory)


def empo_build_function(directory: str, git_dir: str):
    print("=" * 40, "empo_build", "=" * 40)
    print(os.getcwd(), directory)
    print("=" * 99)
    os.chdir(directory)

    # Start editor
    run_command("windsurf .")

    # Copy envs
    commands = [
        "echo 'copying envs';",
        f"cp {git_dir}/../env/.env.server {directory}/sources/server/.env;",
        f"cp {git_dir}/../env/.env.app {directory}/sources/app/.env;",
    ]
    for command in commands:
        run_command(command)

    # Install packages
    install_commands = [
        "corepack enable;",
        "yarn set version 1.22.21;",
        "echo 'node:'",
        "node --version;",
        "echo 'yarn:'",
        "yarn --version;",
        "yarn install --ignore-engine;",
        "cd sources/server; yarn add sharp --ignore-engines;",
    ]
    for command in install_commands:
        run_command(command)
