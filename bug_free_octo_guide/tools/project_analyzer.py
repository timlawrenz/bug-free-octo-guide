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
                    # For now, we'll just read the first 20 lines of each file.
                    # In a real implementation, we would use a language model to summarize.
                    summaries[file_path] = "".join(f.readlines()[:20])
            else:
                summaries[file_path] = f"File not found: {file_path}"

        return summaries