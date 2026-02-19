# CLAUDE.md

**Vault:** `C:\Users\Chris.Isaacson\Vault\projects\batch-resize\README.md`

## Overview

CLI tool for batch resizing images. Reads all supported images from an input
folder, resizes them (by exact dimensions, aspect-preserving fit, or percentage
scale), and writes them to an output folder. Single-file Python script.

## Tech Stack

- **Python** (venv at `env/`)
- **Pillow (PIL)** -- image loading, resizing (LANCZOS), saving
- **argparse** -- CLI interface
- Visual Studio solution file (`batch_resize.sln`) for editing

## Project Structure

```
batch_resize.py      # Entire tool -- CLI parsing, resize logic, batch loop
In/                  # Sample input images (PNG theme screenshots)
env/                 # Local Python venv (Pillow installed here)
README.md
```

## How to Run

```bash
# Activate venv
env\Scripts\activate

# Resize to exact dimensions
python batch_resize.py --in In --out Out --size 180x198

# Resize preserving aspect ratio (fit within bounding box)
python batch_resize.py --in In --out Out --size 180x198 --keep-aspect

# Resize by percentage
python batch_resize.py --in In --out Out --percent 50

# With options
python batch_resize.py --in In --out Out --size 300x300 --overwrite --quality 85 --suffix _thumb
```

## CLI Arguments

| Arg | Required | Description |
|-----|----------|-------------|
| `--in` | yes | Input folder path |
| `--out` | yes | Output folder path (created if missing) |
| `--size` | one of size/percent | Target WxH like `180x198` |
| `--percent` | one of size/percent | Scale factor (e.g. `50` for 50%) |
| `--keep-aspect` | no | Fit within --size box without stretching |
| `--overwrite` | no | Overwrite existing output files |
| `--quality` | no | JPEG quality 1-95 (default 92) |
| `--suffix` | no | Append to filename before extension (e.g. `_small`) |

## Key Notes

- Supported formats: jpg, jpeg, png, bmp, tif, tiff, webp, gif
- `--size` and `--percent` are mutually exclusive
- JPEG outputs auto-convert to RGB if needed, with `optimize=True`
- Uses `Image.LANCZOS` resampling for quality
- Non-recursive: only processes files directly in `--in`, not subdirs
- Errors on individual files are caught and printed, processing continues
