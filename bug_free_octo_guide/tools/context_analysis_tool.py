import os
import subprocess
import tempfile

def analyze_repo(repo_url: str) -> dict:
    """
    Analyzes a GitHub repository by cloning it and summarizing key files.

    Args:
        repo_url: The URL of the GitHub repository to analyze.

    Returns:
        A dictionary containing the summaries of key files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, tmpdir],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            return {"error": f"Failed to clone repository: {e.stderr}"}

        summaries = {}
        files_to_summarize = [
            "db/schema.rb",
            "config/routes.rb",
            "Gemfile",
            "conventions.md",
        ]

        for file_path in files_to_summarize:
            full_path = os.path.join(tmpdir, file_path)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    summaries[file_path] = "".join(f.readlines()[:20])
            else:
                summaries[file_path] = f"File not found: {file_path}"

        return summaries