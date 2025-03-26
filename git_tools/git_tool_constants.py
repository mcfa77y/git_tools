from typing import Callable

from InquirerPy.base.control import Choice

from build_fn import empo_build_function, neatleaf_build

NEATLEAF_PROFILE = "NEATLEAF"
EMPO_PROFILE = "EMPO"
QC_PROFILE = "QC"

PROFILE_NAME = EMPO_PROFILE


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
        "BUILD_FN": neatleaf_build,
    },
    EMPO_PROFILE: {
        "GIT_DIR": "/Users/joe/Projects/empo_health/remote-health-link",
        "WORKTREE_DIR": "/Users/joe/Projects/empo_health/empo-worktrees",
        "DIR_OPTIONS": ["root"],
        "DEFAULT_DIR": "root",
        "BUILD_FN": empo_build_function,
    },
}

ROOT_DIR = "root"

PROFILE = CONSTANTS_MAP[PROFILE_NAME]
WORKTREE_DIR = PROFILE["WORKTREE_DIR"]
GIT_DIR = PROFILE["GIT_DIR"]
DIR_OPTIONS = PROFILE["DIR_OPTIONS"]
BUILD_FN: Callable[[str, str], None] = PROFILE["BUILD_FN"]
PROFILE_DEFAULT_DIR = PROFILE["DEFAULT_DIR"]
IS_VERBOSE = False
DIR_CHOICES = [Choice(value=dir, name=dir) for dir in DIR_OPTIONS]
