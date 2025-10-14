import os
import re
from dotenv import load_dotenv
from langchain_community.document_loaders import GithubFileLoader  # updated import

load_dotenv()
token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

# GitHub repo and README file
repo_name = "Tech-at-DU/ACS-1700-Web-Foundations"
file_path = "README.md"

# Load README.md using updated GithubFileLoader
loader = GithubFileLoader(
    repo=repo_name,  # new argument name
    file_path=file_path,
    access_token=token,
    file_filter=None,  # required in new version
)

documents = loader.load()
print(f"Loaded {len(documents)} documents from {file_path}.")

# Combine all content
content = "\n".join(doc.page_content for doc in documents)

# Extract Schedule section
schedule_pattern = re.compile(
    r"(?:##\s*Schedule\s*)(.*?)(?:##\s|$)", re.DOTALL | re.IGNORECASE
)
match = schedule_pattern.search(content)

if match:
    schedule_text = match.group(1)
    # Extract all URLs (plain URLs and markdown links)
    urls_plain = re.findall(r"https?://[^\s\)]+", schedule_text)
    urls_md = re.findall(r"\[.*?\]\((https?://[^\s\)]+)\)", schedule_text)

    all_links = list(set(urls_plain + urls_md))  # remove duplicates

    print("Links found in Schedule section:")
    for link in all_links:
        print(link)
else:
    print("No Schedule section found in README.md.")
