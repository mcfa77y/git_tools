import os

from InquirerPy.base.control import Choice

from utils import run_command

NEATLEAF_PROFILE = "NEATLEAF"
EMPO_PROFILE = "EMPO"

PROFILE_NAME = EMPO_PROFILE


def default_build_function(directory: str):
    # Change to the selected directory
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


def copy_husky_dir():
    os.makedirs(".husky/_", exist_ok=True)
    print("[worktree add] copy husky dir")
    run_command(f"cp {GIT_DIR}/.husky/_/husky.sh .husky/_/")
    # print("[worktree add] create .git dir")
    # os.makedirs(".git", exist_ok=True)


def neatleaf_build(directory: str):
    copy_husky_dir()
    run_command(f"cp {GIT_DIR}/dashboard/.env dashboard")
    default_build_function(directory)


def empo_build(directory: str):
    os.chdir(directory)
    if not os.path.exists("yarn.lock"):
        print("[constants] empo_build] no yarn.lock")
        return

    commands = [
        "code .",
        f"cp {GIT_DIR}/sources/server/.env sources/server",
        f"cp {GIT_DIR}/sources/app/.env sources/app"
        "corepack enable",
        "echo 'node: $(node --version) \nyarn: $(yarn --version)'"
        "empo_install"
    ]
    for command in commands:
        run_command(command)


CONSTANTS_MAP = {
    NEATLEAF_PROFILE: {
        "GIT_DIR": "/Users/joe/Projects/faux-neatleaf",
        "WORKTREE_DIR": "/Users/joe/Projects/nl-worktrees",
        "DIR_OPTIONS": [
            "dashboard",
            "fleet_management",
            "devops",
            "playground/joe/create_new_user",
            "nx",
            "hasura_tools",
            "cloud_tools",
            "dashboard_api",
            "data_pipeline",
            "databases/migrations/",
            "databases",
            "devops",
            "fleet/fleet_api",
            "fleet/fleet_client",
            "fleet/spyder_client",
            "fleet",
            "fleet_management",
            "landingpage",
            "playground",
            "shared",
            "spyder",
            "spyder_api",
            "playground/joe/aws_tools_v2",
            "playground/joe/bit_bucket_tools",
            "playground/joe/copy-protos",
            "playground/joe/copy_protos",
            "playground/joe/create_new_user",
            'playground/joe/"filter-s3"',
            "playground/joe/flask_aws_test",
            "playground/joe/hasura_tools",
            "playground/joe/migration_test_ground",
            "playground/joe/prune-branches",
            "playground/joe/prune_branches_old",
        ],
        "DEFAULT_DIR": "dashboard",
        "BUILD_FN": default_build_function,
    },
    EMPO_PROFILE: {
        "GIT_DIR": "/Users/joe/Projects/empo_health/remote-health-link",
        "WORKTREE_DIR": "/Users/joe/Projects/empo_health/empo-worktrees",
        "DIR_OPTIONS": ["root", "sources/server", "sources/app"],
        "DEFAULT_DIR": "root",
        "BUILD_FN": empo_build
    },
}

ROOT_DIR_CHOICE = "root"

PROFILE = CONSTANTS_MAP[PROFILE_NAME]
WORKTREE_DIR = PROFILE["WORKTREE_DIR"]
GIT_DIR = PROFILE["GIT_DIR"]
DIR_OPTIONS = PROFILE["DIR_OPTIONS"]
BUILD_FN = PROFILE["BUILD_FN"]

DEFAULT_DIR = PROFILE["DEFAULT_DIR"]
DEBUG = False
DIR_CHOICES = [Choice(value=dir, name=dir) for dir in DIR_OPTIONS]
