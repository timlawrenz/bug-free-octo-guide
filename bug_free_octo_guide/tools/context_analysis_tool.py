# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import subprocess
import tempfile
import logging

def analyze_repo(prompt: str) -> dict:
    """
    Analyzes a GitHub repository by cloning it and summarizing key files.
    The analysis is considered successful even if no specific files are found,
    as long as the repository is successfully cloned.
    """
    match = re.search(r"https://github.com/[\w-]+/[\w-]+", prompt)
    if not match:
        return {
            "success": False,
            "error": "Could not find a GitHub repository URL in the prompt."
        }
    repo_url = match.group(0)

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            logging.info(f"Cloning repository: {repo_url}")
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, tmpdir],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            logging.info("Repository cloned successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone repository: {e.stderr}")
            return {
                "success": False,
                "error": f"Failed to clone repository: {e.stderr}"
            }

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
                summaries[file_path] = "File not found."

        return {
            "success": True,
            "message": "Repository analysis complete.",
            "summaries": summaries
        }
