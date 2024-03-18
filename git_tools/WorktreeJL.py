from dataclasses import dataclass


@dataclass
class WorkTreeJL:
    path: str
    commit_hash: str
    name: str

    def __post_init__(self):
        self.path = self.path.strip()
        self.name = self.name.strip().replace('[', '').replace(']', '')
