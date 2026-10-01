from app.schemas import ComicLayoutPanel, PanelStory


def build_comic_layout(
    stories: list[PanelStory],
    image_paths: list[str],
) -> list[ComicLayoutPanel]:
    if len(stories) != len(image_paths):
        raise ValueError("The number of story panels and images must match.")

    return [
        ComicLayoutPanel(
            panel_number=story.panel_number,
            title=story.title,
            image_path=image_paths[index],
            scene_description=story.scene_description,
            caption=story.caption,
            narration=story.narration,
            dialogue=story.dialogue,
            image_prompt=story.image_prompt,
        )
        for index, story in enumerate(stories)
    ]
