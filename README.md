# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that turns a user's story idea into a five-panel comic. It follows the supplied project documentation: structured outline generation, story/narration generation, Stable Diffusion panel images, layout construction, preview, and PDF export.

## Architecture

```text
Browser
  │
  ▼
FastAPI routes
  ├── Gemini outline generation
  ├── Gemini story/dialogue generation
  ├── Stable Diffusion image generation
  ├── Layout builder
  └── FPDF PDF exporter
  │
  ▼
Jinja2 templates + /static assets
```

The supplied documentation names the legacy `google-generativeai` SDK and Gemini 1.5 Flash/Pro. This implementation keeps the same Flash/Pro responsibilities but uses Google's current `google-genai` SDK, which Google recommends for new Python integrations. Model names are configurable through `.env`.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── comic_service.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   └── exporters.py
│   └── utils/
│       ├── __init__.py
│       └── files.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   ├── export_success.html
│   └── error.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── panels/.gitkeep
│   └── exports/.gitkeep
├── tests/
│   ├── test_app.py
│   └── test_services.py
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## 1. Requirements

- Python 3.10+ (3.11 recommended)
- A Google Gemini API key for real story generation
- A machine capable of running Stable Diffusion locally, preferably an NVIDIA GPU with sufficient VRAM
- Hugging Face access/token if the selected model requires it
- Git and VS Code are recommended

The application also has `LLM_PROVIDER=mock` and `IMAGE_PROVIDER=placeholder` modes for development/testing without external AI credentials.

## 2. Windows / VS Code setup

Open the project folder in VS Code and open **Terminal → New Terminal**.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy the environment template:

```powershell
copy .env.example .env
```

For a no-key smoke test, set:

```env
LLM_PROVIDER=mock
IMAGE_PROVIDER=placeholder
```

Then:

```powershell
python run.py
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## 3. Real Gemini + Stable Diffusion setup

Edit `.env`:

```env
LLM_PROVIDER=gemini
IMAGE_PROVIDER=diffusers
GEMINI_API_KEY=your_key_here
HF_TOKEN=your_huggingface_token_if_needed
```

The documentation originally specifies Gemini 1.5 Flash for outlines and Gemini 1.5 Pro for detailed story generation. Those values can still be configured if your API account exposes them:

```env
GEMINI_OUTLINE_MODEL=gemini-1.5-flash
GEMINI_STORY_MODEL=gemini-1.5-pro
```

For a current Gemini account, use model IDs available to that account, for example:

```env
GEMINI_OUTLINE_MODEL=gemini-2.5-flash
GEMINI_STORY_MODEL=gemini-2.5-pro
```

Do not commit `.env`.

### Stable Diffusion

The default model is:

```env
SD_MODEL_ID=runwayml/stable-diffusion-v1-5
```

The first image-generation request downloads model weights and may take a long time. The files are cached by Hugging Face after the first download.

If the computer has a CUDA GPU:

```env
TORCH_DEVICE=cuda
```

For Apple Silicon:

```env
TORCH_DEVICE=mps
```

For CPU testing:

```env
TORCH_DEVICE=cpu
```

CPU generation is normally very slow; use `IMAGE_PROVIDER=placeholder` for routine development tests.

## 4. Generate a comic

1. Start the server.
2. Open http://127.0.0.1:8000.
3. Enter:
   - Story prompt
   - Character name
   - Setting
   - Tone
   - Art style
4. Click **Create Comic**.
5. Review the five panels.
6. Click **Download Your Comic as PDF**.

The generated PNG files are written to `static/panels/`, and PDFs are written to `static/exports/`.

## 5. API

### POST `/generate-comic/json`

Example:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest.",
  "character_name": "Lumi",
  "setting": "enchanted forest",
  "tone": "dramatic",
  "art_style": "comic book"
}
```

The response contains the five-panel layout and PDF URL.

### POST `/test-image`

```json
{
  "prompt": "A brave fox in an enchanted forest, comic book illustration"
}
```

### GET `/health`

Returns service status.

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 6. Testing

Use mock providers so tests do not require external APIs or a GPU:

```powershell
$env:LLM_PROVIDER="mock"
$env:IMAGE_PROVIDER="placeholder"
pytest -q
```

Or put those values in `.env`.

## 7. Troubleshooting

### `ModuleNotFoundError`
Activate the virtual environment and run:

```powershell
pip install -r requirements.txt
```

### Gemini authentication error
Check:

```env
GEMINI_API_KEY=...
LLM_PROVIDER=gemini
```

### Gemini model not found
The project deliberately makes model IDs configurable. List the models available to your API account or change `GEMINI_OUTLINE_MODEL` and `GEMINI_STORY_MODEL` in `.env`.

### Hugging Face access/download error
Set `HF_TOKEN` if required by the selected model, accept the model's license on Hugging Face where applicable, and retry.

### Stable Diffusion is too slow
Use a CUDA-capable GPU, reduce image dimensions/steps, or use:

```env
IMAGE_PROVIDER=placeholder
```

for frontend/backend development.

### PDF cannot be opened
Make sure the image files exist and that Pillow/FPDF2 installed correctly:

```powershell
pip install --upgrade Pillow fpdf2
```

## 8. Production considerations

This starter project is intentionally local and single-user. Before public deployment, add authentication, persistent storage, job queues, rate limits, request-size limits, cloud object storage, monitoring, secret management, and background workers for AI generation.
