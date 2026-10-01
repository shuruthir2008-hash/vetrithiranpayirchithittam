from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import settings
from app.utils.files import safe_filename


class ImageGenerator:
    """Stable Diffusion image service with a deterministic placeholder test mode."""

    _pipeline = None

    def _device(self) -> str:
        if settings.torch_device != "auto":
            return settings.torch_device

        import torch

        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        if settings.image_provider != "diffusers":
            return None

        import torch
        from diffusers import StableDiffusionPipeline

        dtype = torch.float16 if self._device() == "cuda" else torch.float32

        kwargs = {"torch_dtype": dtype}
        if settings.hf_token:
            kwargs["token"] = settings.hf_token

        self._pipeline = StableDiffusionPipeline.from_pretrained(
            settings.sd_model_id,
            **kwargs,
        )
        self._pipeline = self._pipeline.to(self._device())

        if self._device() == "cuda":
            self._pipeline.enable_attention_slicing()

        return self._pipeline

    def generate_image(self, prompt: str, panel_number: int) -> Path:
        settings.panels_dir.mkdir(parents=True, exist_ok=True)
        filename = safe_filename(f"panel-{panel_number}")
        output = settings.panels_dir / filename

        if settings.image_provider == "placeholder":
            self._create_placeholder(prompt, panel_number, output)
            return output

        pipeline = self._load_pipeline()
        result = pipeline(
            prompt=prompt,
            num_inference_steps=settings.sd_steps,
            guidance_scale=settings.sd_guidance_scale,
            width=settings.image_width,
            height=settings.image_height,
        )
        result.images[0].save(output)
        return output

    def _create_placeholder(self, prompt: str, panel_number: int, output: Path) -> None:
        image = Image.new("RGB", (settings.image_width, settings.image_height), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (12, 12, image.width - 12, image.height - 12),
            outline="black",
            width=4,
        )
        title = f"ComicCraft — Panel {panel_number}"
        draw.text((30, 30), title, fill="black")
        wrapped = prompt[:500]
        draw.text((30, 80), wrapped, fill="black")
        image.save(output)
