import os

from utils import run_command, run_commands
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


def print_banner(title: str, message: str):
    message_length = len(message)
    title_length = len(title)
    diff_length = message_length - title_length
    decorator_count = diff_length // 2
    bottom_decorator_count = diff_length + title_length + 2

    print("\n")
    print("=" * decorator_count, title, "=" * decorator_count)
    print(message)
    print("=" * bottom_decorator_count)


def empo_build_function(dest_dir: str, git_dir: str):
    title = "Empo Build"
    message = f"{dest_dir}"
    print_banner(title, message)
    os.chdir(dest_dir)

    # Start editor
    start_editor = [
        "windsurf .;",
        "~/.bun/bin/bun run /Users/joe/Projects/js_for_fun/apply_vs_code_theme/index.ts;",
    ]
    run_commands(start_editor)

    # Create symbolic links for envs
    ENV_DIR = f"{git_dir}/../env"
    create_symbolic_links = [
        "echo 'creating symbolic links for envs';",
        f"ln -sf {ENV_DIR}/.env.server {dest_dir}/sources/server/.env;",
        f"ln -sf {ENV_DIR}/.env.app {dest_dir}/sources/app/.env;",
        "echo 'creating symbolic links for vscode';"
        f"ln -sf {ENV_DIR}/vscode/launch.json {dest_dir}/.vscode/;",
        f"ln -sf {ENV_DIR}/vscode/tasks.json {dest_dir}/.vscode/;",
    ]
    run_commands(create_symbolic_links)

    # Install packages
    install_commands = [
        "corepack enable;",
        "yarn set version 1.22.21;",
        "echo 'node:'",
        "node --version;",
        "echo 'yarn:'",
        "yarn --version;",
        "yarn install --ignore-engine;",
        "cd sources/server; yarn add sharp@0.33.5 --ignore-engines;",
    ]
    run_commands(install_commands)
