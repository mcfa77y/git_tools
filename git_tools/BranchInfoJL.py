from dataclasses import dataclass
from datetime import datetime


@dataclass
class BranchInfoJL:
    name: str
    date: datetime
    author: str

    @property
    def age(self) -> int:
        """Age of branch in days"""
        return (datetime.now() - self.date).days
