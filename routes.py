from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.schemas import ImageTestRequest, PromptRequest
from app.services.comic_service import ComicService
from app.utils.files import relative_static_url


router = APIRouter()
templates = Jinja2Templates(directory=str(settings.templates_dir))
comic_service = ComicService()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@router.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "llm_provider": settings.llm_provider,
        "image_provider": settings.image_provider,
    }


@router.post("/generate")
def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        result = comic_service.generate(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"request": request, **result},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
def generate_comic_json(payload: PromptRequest):
    try:
        return comic_service.generate(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/test-image")
def test_image(payload: ImageTestRequest):
    try:
        path = comic_service.image_service.generate_image(payload.prompt, 0)
        return {
            "status": "ok",
            "image_path": relative_static_url(path, settings.static_dir),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/export-success")
def export_success(request: Request, pdf: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"request": request, "pdf_path": pdf},
    )


@router.get("/download")
def download_pdf(path: str):
    # Only allow downloads from the application's exports directory.
    requested = (settings.static_dir / path.removeprefix("/static/")).resolve()
    exports_dir = settings.exports_dir.resolve()

    if exports_dir not in requested.parents or not requested.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")

    return FileResponse(
        path=requested,
        media_type="application/pdf",
        filename=requested.name,
    )
