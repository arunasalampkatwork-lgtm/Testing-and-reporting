from pathlib import Path
from datetime import datetime
import json
import re

from app.models.project import Project


class ProjectManager:

    def __init__(self, projects_directory: Path):
        self.projects_directory = projects_directory
        self.projects_directory.mkdir(parents=True, exist_ok=True)

    def _make_project_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"PRJ-{timestamp}"

    def _safe_folder_name(self, title: str) -> str:
        name = re.sub(r'[<>:"/\\|?*]', "_", title)
        return name.strip()

    def create_project(self, title: str, date: str) -> Project:

        title = title.strip()

        if not title:
            raise ValueError("Project title cannot be empty.")

        project_id = self._make_project_id()

        folder_name = self._safe_folder_name(title)
        project_folder = self.projects_directory / folder_name

        # Prevent accidental duplicate project folders
        if project_folder.exists():
            raise ValueError(
                f"A project folder named '{title}' already exists."
            )

        project_folder.mkdir(parents=True)

        project = Project(
            project_id=project_id,
            title=title,
            date=date
        )

        self._save_project(project, project_folder)

        return project

    def _save_project(self, project: Project, project_folder: Path):

        project_file = project_folder / "project.json"

        data = {
            "project_id": project.project_id,
            "title": project.title,
            "date": project.date
        }

        with open(project_file, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4
            )

    def load_projects(self) -> list[Project]:

        projects = []

        for folder in self.projects_directory.iterdir():

            if not folder.is_dir():
                continue

            project_file = folder / "project.json"

            if not project_file.exists():
                continue

            try:

                with open(
                    project_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(file)

                project = Project(
                    project_id=data["project_id"],
                    title=data["title"],
                    date=data["date"]
                )

                projects.append(project)

            except (json.JSONDecodeError, KeyError):

                print(
                    f"Warning: Could not load project "
                    f"from {project_file}"
                )

        return projects