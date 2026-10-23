# How to Post This Project on GitHub

A simple step-by-step guide. Do these once.

## 0. One-time setup (only if you've never used git here)
- Install Git: https://git-scm.com/download/win  (if `git --version` fails in a terminal)
- Create a free GitHub account: https://github.com
- Tell git who you are (run once, use your GitHub email):
  ```
  git config --global user.name "Kaviya Dharshini S"
  git config --global user.email "your-github-email@example.com"
  ```

## 1. Create an empty repository on GitHub (in the browser)
1. Go to https://github.com and log in.
2. Click the **+** (top right) → **New repository**.
3. Repository name: `rag-document-qa`
4. Description: `Free local RAG app — ask questions about PDF/Excel documents`
5. Choose **Public** (so others/recruiters can see it).
6. **Do NOT** tick "Add a README" (we already have one).
7. Click **Create repository**.
8. Copy the repo URL shown, e.g. `https://github.com/<your-username>/rag-document-qa.git`

## 2. Push the project (in a terminal)
Open a terminal in the project folder and run these one by one:

```powershell
cd C:\Users\kaviya.dharshini\rag-document-qa

git init                       # start tracking this folder with git
git add .                      # stage all files (the .gitignore keeps out .env, venv, .gguf)
git commit -m "RAG Document Q&A: PDF/Excel question answering (local, free)"
git branch -M main
git remote add origin https://github.com/<your-username>/rag-document-qa.git
git push -u origin main
```

- When it asks to sign in, a browser window opens — log in to GitHub to authorize. (First push only.)

## 3. Verify
- Refresh your GitHub repo page in the browser — you should see all the files and the README displayed.

## What gets uploaded vs skipped
UPLOADED: loader.py, rag.py, main.py, app.py, requirements.txt, README.md, Modelfile,
          .env.example, .gitignore, data/ (sample files)
SKIPPED (by .gitignore, correctly): .env (secrets), venv/ (libraries), *.gguf (468 MB model), __pycache__/

## If you change files later and want to update GitHub
```powershell
git add .
git commit -m "describe what you changed"
git push
```

## Tips
- The README is the first thing people see — it's already written to explain the project well.
- Keep the repo PUBLIC so it counts for your portfolio / future opportunities.
- Never commit the real `.env` (it's already git-ignored — good).
