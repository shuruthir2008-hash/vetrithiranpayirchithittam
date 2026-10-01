import json
from typing import Any

from app.config import settings
from app.schemas import PanelOutline


class GeminiFlashService:
    """Creates a structured five-panel outline."""

    def __init__(self) -> None:
        self.client = None

    def _get_client(self):
        if settings.llm_provider != "gemini":
            return None
        if self.client is None:
            if not settings.gemini_api_key:
                raise RuntimeError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini.")
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)
        return self.client

    def generate_outline(
        self,
        story_prompt: str,
        character_name: str,
        setting: str,
        tone: str,
        art_style: str,
    ) -> list[PanelOutline]:
        if settings.llm_provider == "mock":
            return self._mock_outline(
                story_prompt, character_name, setting, tone, art_style
            )

        prompt = f"""
Create a coherent {settings.panel_count}-panel comic outline.

User story idea: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY a JSON array. Each item must contain:
panel_number (integer), title (string), scene_description (string),
image_prompt (string).

Keep character identity, clothing, setting, time of day, and visual continuity
consistent across panels. Make each image_prompt detailed enough for Stable
Diffusion. Do not put dialogue in the outline.
""".strip()

        from google.genai import types

        response = self._get_client().models.generate_content(
            model=settings.gemini_outline_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        data = self._parse_json(response.text)
        if not isinstance(data, list):
            raise ValueError("Gemini outline response was not a JSON array.")

        outlines = [PanelOutline.model_validate(item) for item in data]
        if len(outlines) != settings.panel_count:
            raise ValueError(
                f"Expected {settings.panel_count} panels, received {len(outlines)}."
            )
        return outlines

    @staticmethod
    def _parse_json(text: str) -> Any:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned)

    def _mock_outline(self, story_prompt, character_name, setting, tone, art_style):
        return [
            PanelOutline(
                panel_number=i,
                title=[
                    "The Beginning",
                    "A Strange Discovery",
                    "The Challenge",
                    "The Turning Point",
                    "A New Dawn",
                ][i - 1],
                scene_description=(
                    f"{character_name} experiences the next stage of this story in "
                    f"{setting}. The mood remains {tone}."
                ),
                image_prompt=(
                    f"{character_name}, {setting}, {art_style} comic illustration, "
                    f"consistent character design, panel {i}, cinematic composition"
                ),
            )
            for i in range(1, settings.panel_count + 1)
        ]
