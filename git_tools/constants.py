from InquirerPy.base.control import Choice

WORKTREE_DIR = '/Users/joe/Projects/nl-worktrees'
NEATLEAF_DIR = '/Users/joe/Projects/faux-neatleaf'

dir_options = [
    'dashboard', 'fleet_management', 'devops', 'playground/joe/create_new_user',
    'other', 'cloud_tools', 'dashboard_api', 'data_pipeline', 'databases',
    'devops', 'fleet/fleet_api', 'fleet/fleet_client', 'fleet/spyder_client',
    'fleet', 'fleet_management', 'landingpage', 'playground', 'shared',
    'spyder', 'spyder_api', 'playground/joe/aws_tools_v2',
    'playground/joe/bit_bucket_tools', 'playground/joe/copy-protos',
    'playground/joe/copy_protos', 'playground/joe/create_new_user',
    'playground/joe/"filter-s3"', 'playground/joe/flask_aws_test',
    'playground/joe/hasura_tools', 'playground/joe/migration_test_ground',
    'playground/joe/prune-branches', 'playground/joe/prune_branches_old'
]

DIR_CHOICES = [Choice(value=dir, name=dir) for dir in dir_options]
