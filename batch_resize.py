
import os
import argparse
from pathlib import Path
from PIL import Image

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".gif"}

def parse_size(size_str: str):
    """
    Parse WxH like '180x198' or '180,198' into (180, 198)
    """
    s = size_str.lower().replace(",", "x").strip()
    if "x" not in s:
        raise ValueError("Size must be like 180x198 (or 180,198).")
    w, h = s.split("x", 1)
    return int(w.strip()), int(h.strip())

def resize_one(img: Image.Image, width=None, height=None, scale=None, keep_aspect=False):
    """
    Resize logic:
    - If scale provided: multiply original by scale (0.125 for 12.5%)
    - Else use width/height:
        - if keep_aspect: fit inside width x height preserving aspect ratio
        - else: force exactly width x height
    """
    if scale is not None:
        new_w = max(1, int(round(img.width * scale)))
        new_h = max(1, int(round(img.height * scale)))
        return img.resize((new_w, new_h), Image.LANCZOS)

    if width is None or height is None:
        raise ValueError("Width and height must be provided if not using --percent.")

    if keep_aspect:
        copy = img.copy()
        copy.thumbnail((width, height), Image.LANCZOS)  # preserves aspect ratio
        return copy
    else:
        return img.resize((width, height), Image.LANCZOS)

def main():
    parser = argparse.ArgumentParser(
        description="Batch resize images to a fixed size OR by percent scale."
    )
    parser.add_argument("--in", dest="input_dir", required=True, help="Input folder path")
    parser.add_argument("--out", dest="output_dir", required=True, help="Output folder path")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--size", help="Target size like 180x198 (exact) or max-fit if --keep-aspect")
    group.add_argument("--percent", type=float, help="Percent scale, e.g. 12.5 for 12.5%%")

    parser.add_argument("--keep-aspect", action="store_true",
                        help="If using --size, fit within WxH while preserving aspect ratio (no stretching).")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite files in output folder if they already exist.")
    parser.add_argument("--quality", type=int, default=92,
                        help="JPEG quality (1-95). Used only when saving JPEG. Default 92.")
    parser.add_argument("--suffix", default="",
                        help="Optional suffix added before extension, e.g. _small")

    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists():
        raise SystemExit(f"Input folder does not exist: {in_dir}")

    # Determine mode
    if args.size:
        w, h = parse_size(args.size)
        scale = None
    else:
        if args.percent <= 0:
            raise SystemExit("--percent must be > 0")
        scale = args.percent / 100.0
        w = h = None

    processed = 0
    skipped = 0

    for path in in_dir.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTS:
            continue

        out_name = path.stem + args.suffix + path.suffix
        out_path = out_dir / out_name

        if out_path.exists() and not args.overwrite:
            print(f"Skip (exists): {out_path.name}")
            skipped += 1
            continue

        try:
            with Image.open(path) as img:
                # Keep original mode unless saving as JPEG requires RGB
                resized = resize_one(
                    img,
                    width=w,
                    height=h,
                    scale=scale,
                    keep_aspect=args.keep_aspect
                )

                save_kwargs = {}
                # If output is jpg/jpeg, ensure RGB and apply quality
                if out_path.suffix.lower() in {".jpg", ".jpeg"}:
                    if resized.mode not in ("RGB", "L"):
                        resized = resized.convert("RGB")
                    save_kwargs["quality"] = max(1, min(95, args.quality))
                    save_kwargs["optimize"] = True

                resized.save(out_path, **save_kwargs)
                processed += 1
                print(f"Saved: {out_path.name}")

        except Exception as e:
            print(f"Error processing {path.name}: {e}")

    print(f"\nDone. Processed: {processed}, Skipped: {skipped}, Output: {out_dir}")

if __name__ == "__main__":
    main()

