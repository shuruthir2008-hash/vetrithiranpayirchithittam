import os

os.environ["LLM_PROVIDER"] = "mock"
os.environ["IMAGE_PROVIDER"] = "placeholder"

from app.services.gemini_flash import GeminiFlashService
from app.services.gemini_pro import GeminiProService


def test_mock_outline_and_story():
    outline = GeminiFlashService().generate_outline(
        "A fox explores a forest.",
        "Lumi",
        "forest",
        "funny",
        "comic book",
    )
    assert len(outline) == 5

    story = GeminiProService().generate_story(outline, "Lumi", "funny")
    assert len(story) == 5
    assert story[0].dialogue
