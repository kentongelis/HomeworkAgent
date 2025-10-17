from github import Github
import os
from dotenv import load_dotenv

load_dotenv()


def get_repo(path):
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    g = Github(token) if token else Github()

    print(f"Fetching repo: {path}")
    repo = g.get_repo(path)

    folder_path = "Lessons"
    lessons_content = {}

    def fetch_folder(folder):
        contents = repo.get_contents(folder)

        for item in contents:
            if item.type == "dir":
                fetch_folder(item.path)  # recurse into subdirectory
            elif item.name.endswith(".md") and "lab" not in item.name.lower():
                content = item.decoded_content.decode()
                lessons_content[item.name.strip(".md")] = content
                print(f"Fetched: {item.name}")

    fetch_folder(folder_path)
    return lessons_content
