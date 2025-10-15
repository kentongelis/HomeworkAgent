from github import Github
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub setup
token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
g = Github(token) if token else Github()

# Repo info
owner_repo = "Tech-at-DU/ACS-1700-Web-Foundations"
repo = g.get_repo(owner_repo)

# Folder to read
folder_path = "Lessons"

# 1️⃣ Get all files in the folder
contents = repo.get_contents(folder_path)
markdown_files = [file for file in contents if file.name.endswith(".md")]

# 2️⃣ Fetch content for each Markdown file
lessons_content = {}
for md_file in markdown_files:
    content = md_file.decoded_content.decode()
    lessons_content[md_file.name] = content

# 3️⃣ Print or use the content
for filename, content in lessons_content.items():
    print(f"\n===== {filename} =====")
    print(content)  # print first 500 chars only for brevity
    break
