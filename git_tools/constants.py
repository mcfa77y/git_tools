
from InquirerPy.base.control import Choice

CONSTANTS_MAP = {
    'NEATLEAF': {
        'DEFAULT_DIR': 'dashboard',
        'WORKTREE_DIR': '/Users/joe/Projects/nl-worktrees',
        'GIT_DIR': '/Users/joe/Projects/faux-neatleaf',
        'DIR_OPTIONS': [
            'dashboard', 'fleet_management', 'devops', 'playground/joe/create_new_user', 'nx',
            'hasura_tools', 'cloud_tools', 'dashboard_api', 'data_pipeline', 'databases/migrations/', 'databases',
            'devops', 'fleet/fleet_api', 'fleet/fleet_client', 'fleet/spyder_client',
            'fleet', 'fleet_management', 'landingpage', 'playground', 'shared',
            'spyder', 'spyder_api', 'playground/joe/aws_tools_v2',
            'playground/joe/bit_bucket_tools', 'playground/joe/copy-protos',
            'playground/joe/copy_protos', 'playground/joe/create_new_user',
            'playground/joe/"filter-s3"', 'playground/joe/flask_aws_test',
            'playground/joe/hasura_tools', 'playground/joe/migration_test_ground',
            'playground/joe/prune-branches', 'playground/joe/prune_branches_old'
        ]
    },
    'EMPO': {
        'WORKTREE_DIR': '/Users/joe/Projects/empo_health/empo-worktrees',
        'GIT_DIR': '/Users/joe/Projects/empo_health/remote-health-link',
        'DIR_OPTIONS': [
            'sources/server',
            'sources/app',
            ''
        ],
        'DEFAULT_DIR': 'sources/server'
    }}
NEATLEAF_PROFILE = 'NEATLEAF'
EMPO_PROFILE = 'EMPO'

PROFILE = EMPO_PROFILE

WORKTREE_DIR = CONSTANTS_MAP[PROFILE]['WORKTREE_DIR']
GIT_DIR = CONSTANTS_MAP[PROFILE]['GIT_DIR']
DIR_OPTIONS = CONSTANTS_MAP[PROFILE]['DIR_OPTIONS']

DEFAULT_DIR = CONSTANTS_MAP[PROFILE]['DEFAULT_DIR']
DEBUG = False
DIR_CHOICES = [Choice(value=dir, name=dir) for dir in DIR_OPTIONS]
