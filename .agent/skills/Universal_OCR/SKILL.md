---
name: Universal_OCR
description: Perform OCR on any image or PDF locally using GLM-OCR running via MLX on Apple Silicon. Extracts text, tables, formulas, and structured content into Markdown format.
---

# Universal OCR (GLM-OCR via MLX)

This skill uses a locally running GLM-OCR model to extract text and structured content from images and PDFs. It runs entirely on the user's M1 iMac — no internet or API key needed.

## Prerequisites

1. The external disk `/Volumes/External Disk` is **plugged in**
2. The MLX server is **running** in the background

**The server is a persistent process — start it once and leave it running.** It uses zero CPU/GPU when idle, so it won't slow down the machine. You only need to restart it after a reboot or if the external disk was unplugged.

To start the server (one-time, keep this terminal open):

```bash
HF_HOME="/Volumes/External Disk/GLM-OCR/huggingface" "/Volumes/External Disk/GLM-OCR/mlx-env/bin/mlx_vlm.server" --trust-remote-code
```

Once running, **do not stop it**. All OCR calls will use it instantly with no startup delay.

## When to Use

- When the user provides an image (`.png`, `.jpg`, `.jpeg`, `.webp`) or PDF and wants its text extracted
- When the user says "read this image", "extract text", "OCR this", or "what does this say"
- When you need to process a document, screenshot, table, formula, or handwritten content programmatically

## How to Run OCR

### Method 1: Python API (preferred for programmatic use)

```python
import sys
sys.path.insert(0, "/Volumes/External Disk/GLM-OCR/sdk-env/lib/python3.14/site-packages")

from glmocr import GlmOcr

with GlmOcr(config_path="/Volumes/External Disk/GLM-OCR/config.yaml") as ocr:
    result = ocr.parse("/absolute/path/to/image.png")
    print(result.markdown_result)
    # Optionally save output:
    result.save(output_dir="./ocr-output")
```

Replace `/absolute/path/to/image.png` with the actual file path.

### Method 2: CLI (for quick one-off use)

```bash
"/Volumes/External Disk/GLM-OCR/sdk-env/bin/glmocr" parse "/absolute/path/to/image.png" \
  --config "/Volumes/External Disk/GLM-OCR/config.yaml" \
  --output "./ocr-output"
```

## Output

- `result.markdown_result` — the extracted content as a Markdown string
- `result.save(output_dir=...)` — saves Markdown + JSON layout details to a folder
- Output includes: plain text, tables (as Markdown tables), formulas (LaTeX), code blocks

## Config Location

```
/Volumes/External Disk/GLM-OCR/config.yaml
```

Current config connects to the local MLX server at `localhost:8080`.

## File Structure Reference

```
/Volumes/External Disk/GLM-OCR/
├── mlx-env/        ← MLX inference engine (Terminal 1)
├── sdk-env/        ← GLM-OCR SDK (run OCR from here)
├── config.yaml     ← SDK configuration
└── huggingface/    ← Downloaded model weights (~1-2 GB)
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` | MLX server is not running — start it in Terminal 1 |
| `model glm_ocr not found` | Reinstall mlx-vlm from git: `pip install git+https://github.com/Blaizzy/mlx-vlm.git` |
| `External Disk not found` | Plug in the external disk |
| Slow first response | Normal — MLX compiles Metal shaders on first run. Subsequent calls are faster. |
| Out of memory | Close other apps. The model only needs ~2 GB of unified memory. |

## Notes

- Supports: images (PNG, JPG, WEBP), PDFs
- Best at: complex tables, formulas, code, Chinese/English mixed text, seals
- Model: `mlx-community/GLM-OCR-bf16` (0.9B parameters, runs fully on M1 GPU via Metal)
- No data leaves the machine — fully local and private
