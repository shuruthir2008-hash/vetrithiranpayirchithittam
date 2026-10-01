import json

from app.config import settings
from app.schemas import PanelOutline, PanelStory


class GeminiProService:
    """Expands the outline into narration, captions, and dialogue."""

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

    def generate_story(
        self,
        outline: list[PanelOutline],
        character_name: str,
        tone: str,
    ) -> list[PanelStory]:
        if settings.llm_provider == "mock":
            return [
                PanelStory(
                    panel_number=p.panel_number,
                    title=p.title,
                    scene_description=p.scene_description,
                    image_prompt=p.image_prompt,
                    caption=f"A {tone} moment unfolds.",
                    narration=(
                        f"{character_name} takes a careful step forward, discovering "
                        f"that every choice can change the adventure."
                    ),
                    dialogue=[f"{character_name}: We can do this!"],
                )
                for p in outline
            ]

        outline_json = json.dumps(
            [p.model_dump() for p in outline], ensure_ascii=False, indent=2
        )
        prompt = f"""
Expand the following comic outline into polished comic writing.

Main character: {character_name}
Tone: {tone}

Outline:
{outline_json}

Return ONLY a JSON array with one item per panel. Every item must contain:
panel_number, title, scene_description, image_prompt, caption, narration,
dialogue (an array of short dialogue strings).

Keep the same panel order and visual continuity. Dialogue should be short enough
to fit in comic speech bubbles. Do not introduce a different protagonist.
""".strip()

        from google.genai import types

        response = self._get_client().models.generate_content(
            model=settings.gemini_story_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )

        cleaned = response.text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]

        data = json.loads(cleaned)
        stories = [PanelStory.model_validate(item) for item in data]
        if len(stories) != len(outline):
            raise ValueError("Story generation returned an unexpected panel count.")
        return stories
