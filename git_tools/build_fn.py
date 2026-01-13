import os

from logger.logger import Logger
from utils import run_command, run_commands

logger = Logger("build_fn").logger_jl


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


def copy_husky_dir(git_dir: str):
    os.makedirs(".husky/_", exist_ok=True)
    print("[build_fn] copy husky dir")
    run_command(f"cp {git_dir}/.husky/_/husky.sh .husky/_/")


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
    # editor = "cursor"
    editor = "windsurf"
    start_editor = [
        f"{editor} .;",
        "~/.bun/bin/bun run /Users/joe/Projects/js_for_fun/apply_vs_code_theme/index.ts;",
    ]
    run_commands(start_editor)
    # Create symbolic links for envs
    env_dir = f"{git_dir}/../env"
    create_symbolic_links = [
        "echo 'creating symbolic links for envs';",
        f"ln -sf {env_dir}/.env.server {dest_dir}/modules/backend-api/.env;",
        f"ln -sf {env_dir}/.env.app {dest_dir}/modules/frontend-app/.env;",
        f"ln -sf {env_dir}/.env.qa {dest_dir}/modules/qa/.env;",
        f"ln -sf {env_dir}/.env.rhl-api-tools {dest_dir}/modules/helper-scripts/rhl-api-tools/.env;",
        "echo 'creating symbolic links for vscode';"
        f"ln -sf {env_dir}/vscode/launch.json {dest_dir}/.vscode/;",
        f"ln -sf {env_dir}/vscode/tasks.json {dest_dir}/.vscode/;",
        # "echo 'creating symbolic links for terraform';"
        # f"ln -sf {env_dir}/terraform/.envrc.stacks.production {dest_dir}/infrastructure/stacks/production/.envrc;",
        # f"ln -sf {env_dir}/terraform/.envrc.stacks.staging {dest_dir}/infrastructure/stacks/staging/.envrc;",
    ]
    run_commands(create_symbolic_links)

    # Install packages
    install_commands = [
        # "source $HOME/.nvm/nvm.sh && nvm use 22 && corepack enable",
        "yarn set version 4.7.0",
        'echo "node: $(node --version)"',
        'echo "yarn: $(yarn --version)"',
        "yarn install",
    ]
    run_commands(install_commands)
