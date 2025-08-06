import os
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.genai.types import Part
import datetime
import re

class PrdAgent(LlmAgent):
    feature_description: str

    def __init__(self, llm: BaseLlm, feature_description: str):
        super().__init__(
            model=llm,
            name="prd_agent",
            instruction="You are a product manager. Your task is to write a Product Requirements Document (PRD) based on the provided feature description.",
            feature_description=feature_description
        )

    def load_prompt(self) -> str:
        """
        Loads the prompt from the prdprompt.md file.
        """
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prdprompt.md")
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt.replace("[Engineer: Provide a concise name for the feature]", self.feature_description)

    async def generate_prd(self, feature_description: str) -> str:
        """Generates a PRD and saves it as an artifact."""
        prompt = self.load_prompt()
        response = await self.model.generate_content(prompt)
        prd_content = response.text

        # Save the PRD to a file
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        sanitized_feature = re.sub(r'\W+', '-', feature_description).lower()
        file_name = f"{timestamp}-{sanitized_feature}.md"
        artifact_dir = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "prd")
        os.makedirs(artifact_dir, exist_ok=True)
        file_path = os.path.join(artifact_dir, file_name)
        
        with open(file_path, "w") as f:
            f.write(prd_content)
        
        return prd_content
