# Task Automation Research Agent (MLOps Experiment 10)

A Streamlit application that searches the web for a user-provided topic and returns a concise three-point research brief. It includes Docker packaging, pytest checks, GitHub Actions CI, Hugging Face Spaces deployment automation, and basic application logging.

## Important notes
- Add `OPENAI_API_KEY` only in your local environment or Hugging Face Space Settings → Variables and secrets. Never commit it.
- This project uses `gpt-4o-mini` by default rather than the legacy `gpt-3.5-turbo` named in the lab handout. You can change `OPENAI_MODEL` in the hosting secrets if your account supports a different model.
- Without an OpenAI key, the app can still show the top three search snippets for interface testing; this is not an AI-generated summary.
- This is a prepared standalone implementation. If Experiment 9 has a required custom search/summarization workflow, merge that logic into `app.py` before submission.

## Run locally (Windows PowerShell)
1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Create and activate a virtual environment:
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Set the API key for this terminal session (optional for snippet-only testing):
   ```powershell
   $env:OPENAI_API_KEY="YOUR_KEY_HERE"
   ```
6. Start the app:
   ```powershell
   streamlit run app.py
   ```
7. Open the local address printed in the terminal, usually `http://localhost:8501`.

## Test and Docker
```powershell
pytest -v
docker build -t task-automation-agent .
docker run --rm -p 7860:7860 -e OPENAI_API_KEY="YOUR_KEY_HERE" task-automation-agent
```
Then open `http://localhost:7860`. Docker is optional for creating the free hosted Space, but the lab asks for a Docker build and local container test; use a machine with Docker if available.

## Deploy free on Hugging Face Spaces
1. Sign in at https://huggingface.co/ and create a new **Space**.
2. Choose **Docker** as the Space SDK and a CPU/free hardware option if available.
3. Set the Space name, for example `task-automation-agent`. The full ID is `YOUR_USERNAME/task-automation-agent`.
4. In Space **Settings → Variables and secrets**, add secret `OPENAI_API_KEY` with your own key. Optionally add variable `OPENAI_MODEL` = `gpt-4o-mini`.
5. In GitHub, create a repository and upload this project's files to its `main` branch.
6. In the GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**:
   - `HF_TOKEN`: a Hugging Face access token with write permission for the Space.
   - `HF_SPACE_ID`: the full Space ID, e.g. `YOUR_USERNAME/task-automation-agent`.
7. Push a commit to `main`. The `CI - Test and Build` workflow runs tests and builds the Docker image. The deployment workflow uploads the app files to the Space; the Space then builds and starts the Docker app.
8. Open the Space page and wait for its status to become **Running**. The public URL is usually `https://YOUR_USERNAME-task-automation-agent.hf.space` (confirm it from the Space page).

## GitHub upload options
Recommended: create an empty GitHub repository, then upload the extracted project files through the GitHub website, preserving the `.github/workflows` folders. Alternatively use Git in this folder:
```powershell
git init
git add .
git commit -m "Add research agent and MLOps workflow"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

## Screenshots for the report
Capture your actual screens (do not fabricate screenshots):
1. Streamlit app home page.
2. A generated brief for topic 1.
3. A generated brief for topic 2.
4. GitHub repository file list.
5. GitHub Actions CI workflow showing success.
6. Hugging Face Space Settings with the secret name visible but the secret value hidden.
7. Hugging Face Space running with its public URL.
8. Space runtime/build logs showing request logs and a typical request time.
9. Docker build/run output if you have access to Docker.

## Troubleshooting
- **No AI summary:** Check `OPENAI_API_KEY` is set in the hosting Space secrets, and confirm the account has API access/credits.
- **Model not found / access denied:** Set `OPENAI_MODEL` to a model available to your API account.
- **Space build fails:** Open the Space **Logs** tab and fix the first dependency or startup error.
- **GitHub deploy workflow fails:** Check that `HF_TOKEN` is a write-enabled token and `HF_SPACE_ID` exactly matches `username/space-name`.
- **Search provider errors/rate limits:** Retry later or adjust the search query. External search availability is not guaranteed.
- **Do not include API key values in screenshots, logs, reports, or Git history.**
