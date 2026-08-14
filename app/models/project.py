from dataclasses import dataclass


@dataclass
class Project:
    project_id: str
    title: str
    date: str