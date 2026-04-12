# HomeworkAgent

A Flask web app that turns a GitHub repository of Markdown lesson files into interactive AI tutors — one per lesson. Students can ask questions about lesson content and take auto-generated quizzes.

## How it works

1. Paste a GitHub repo URL (e.g. `https://github.com/user/repo`) into the home page
2. The app fetches all `.md` files under a `Lessons/` folder in that repo (skipping lab files)
3. Each lesson is embedded into a ChromaDB vector store and wrapped with a `MarkdownTutor`
4. Students can chat with each tutor (RAG-backed Q&A with conversation history) or start a multiple-choice quiz generated from the lesson content

## Stack

- **Backend:** Flask, LangChain, ChromaDB, OpenAI (`gpt-4o-mini` + `text-embedding-ada-002`)
- **GitHub access:** PyGithub
- **Frontend:** Jinja2 templates

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
OPENAI_API_KEY=sk-...
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...   # optional, increases rate limits
```

## Run

```bash
python app.py
```

Open `http://localhost:3000`, paste a GitHub repo URL, and start studying.

## Repo format expected

The target GitHub repo must have a `Lessons/` folder containing `.md` files. Files with "lab" in the name are skipped.
