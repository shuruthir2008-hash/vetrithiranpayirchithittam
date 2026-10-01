from app.config import settings
from app.services.exporters import save_pdf
from app.services.gemini_flash import GeminiFlashService
from app.services.gemini_pro import GeminiProService
from app.services.image_generator import ImageGenerator
from app.services.layout_builder import build_comic_layout
from app.utils.files import relative_static_url


class ComicService:
    def __init__(self) -> None:
        self.outline_service = GeminiFlashService()
        self.story_service = GeminiProService()
        self.image_service = ImageGenerator()

    def generate(
        self,
        story_prompt: str,
        character_name: str,
        setting: str,
        tone: str,
        art_style: str,
    ):
        if len(story_prompt) > settings.max_story_prompt_length:
            raise ValueError(
                f"Story prompt must be at most {settings.max_story_prompt_length} characters."
            )

        outline = self.outline_service.generate_outline(
            story_prompt, character_name, setting, tone, art_style
        )
        stories = self.story_service.generate_story(outline, character_name, tone)

        image_paths = []
        for story in stories:
            path = self.image_service.generate_image(
                story.image_prompt,
                story.panel_number,
            )
            image_paths.append(relative_static_url(path, settings.static_dir))

        layout = build_comic_layout(stories, image_paths)
        title = f"{character_name}'s Comic"
        pdf_path = save_pdf(title, layout)
        pdf_url = relative_static_url(pdf_path, settings.static_dir)

        return {
            "title": title,
            "layout": layout,
            "pdf_path": pdf_url,
        }
