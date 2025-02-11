
import os

from utils import run_command


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
    if not os.path.exists("yarn.lock"):
        print("[build_fn] empo_build] no yarn.lock")
        return

    commands = [
        "windsurf .;",
        "echo 'copying envs';",
        f"cp {git_dir}/sources/server/.env {directory}/sources/server;",
        f"cp {git_dir}/sources/app/.env {directory}/sources/app;"
        "corepack enable;",
        "echo 'node: $(node --version) \nyarn: $(yarn --version)';"
        "yarn install --ignore-engine; cd sources/server; yarn add sharp --ignore-engines; cd ../.."
    ]
    for command in commands:
        run_command(command, is_verbose=True)
