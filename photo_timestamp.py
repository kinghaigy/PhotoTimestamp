#!/usr/bin/env python3
"""
photo_timestamp.py

Recursively processes images in a source folder, reading the EXIF date taken
and stamping it onto the bottom-right corner of each image (25% of image width).
Optionally prints children's names with their age in years and months at the time
the photo was taken.

Usage:
    python photo_timestamp.py <source_folder> [options]

Examples:
    python photo_timestamp.py ./photos
    python photo_timestamp.py ./photos --output ./stamped
    python photo_timestamp.py ./photos --children "Wesley=2000-01-15" "Hazel=2022-04-10"
"""

import argparse
import os
import sys
from datetime import date, datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required. Install it with: pip install Pillow")

try:
    import piexif
except ImportError:
    sys.exit("piexif is required. Install it with: pip install piexif")

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"}

# EXIF date format
EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"


def parse_children(children_args: list[str]) -> list[tuple[str, date]]:
    """Parse children arguments in the format 'Name=YYYY-MM-DD'."""
    children = []
    for arg in children_args:
        try:
            name, dob_str = arg.split("=", 1)
            dob = datetime.strptime(dob_str.strip(), "%Y-%m-%d").date()
            children.append((name.strip(), dob))
        except ValueError:
            print(f"Warning: Could not parse child argument '{arg}'. "
                  f"Expected format: 'Name=YYYY-MM-DD'. Skipping.", file=sys.stderr)
    return children


def compute_age(dob: date, at_date: date) -> tuple[int, int]:
    """Return (years, months) age of someone born on dob at a given date."""
    years = at_date.year - dob.year
    months = at_date.month - dob.month
    if at_date.day < dob.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return years, months


def age_string(name: str, years: int, months: int) -> str:
    """Format the age label, e.g. 'Tom - 2 years, 3 months'."""
    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months > 0:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if not parts:
        parts.append("0 months")
    return f"{name} - {', '.join(parts)}"


def get_exif_date(image: Image.Image, image_path: Path) -> date | None:
    """Extract date taken from EXIF data. Returns None if not available."""
    # Try piexif first (works reliably for JPEG/TIFF)
    try:
        exif_data = piexif.load(str(image_path))
        for tag in (piexif.ExifIFD.DateTimeOriginal, piexif.ExifIFD.DateTimeDigitized):
            value = exif_data.get("Exif", {}).get(tag)
            if value:
                dt = datetime.strptime(value.decode(), EXIF_DATE_FORMAT)
                return dt.date()
        # Fall back to IFD0 DateTime
        value = exif_data.get("0th", {}).get(piexif.ImageIFD.DateTime)
        if value:
            dt = datetime.strptime(value.decode(), EXIF_DATE_FORMAT)
            return dt.date()
    except Exception:
        pass

    # Fallback: try PIL getexif (works for PNG and other formats)
    try:
        exif = image.getexif()
        if exif:
            # 0x9003 = DateTimeOriginal, 0x9004 = DateTimeDigitized, 0x0132 = DateTime
            for tag_id in (0x9003, 0x9004, 0x0132):
                value = exif.get(tag_id)
                if value:
                    dt = datetime.strptime(value, EXIF_DATE_FORMAT)
                    return dt.date()
    except Exception:
        pass

    return None


def load_font(target_px: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load the best available font at approximately target_px size."""
    font_candidates = [
        # Common system fonts (Linux / macOS / Windows)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, target_px)
            except Exception:
                continue
    # Last resort: PIL default bitmap font (fixed size, ignores target_px)
    return ImageFont.load_default()


def stamp_image(
    image_path: Path,
    output_path: Path,
    children: list[tuple[str, date]],
    dry_run: bool,
) -> bool:
    """
    Stamp date (and optional child ages) onto the image.
    Returns True on success.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"  Skipping {image_path.name}: cannot open image ({e})", file=sys.stderr)
        return False

    photo_date = get_exif_date(img, image_path)
    if photo_date is None:
        print(f"  Skipping {image_path.name}: no EXIF date found.")
        return False

    img_w, img_h = img.size

    # Target font size: text block should be ~33% of image width
    # We fit the date line at full target width and scale accordingly.
    target_text_width = img_w * 0.33

    # Build the text lines
    date_line = f"{photo_date.day}/{photo_date.month}/{photo_date.year}"
    age_lines = []
    for name, dob in children:
        if photo_date >= dob:
            years, months = compute_age(dob, photo_date)
            age_lines.append(age_string(name, years, months))

    all_lines = [date_line] + age_lines

    # Binary-search for the right font size so the longest line is ~33% img width.
    # Always size against ALL children (using a fixed representative age) so the font
    # stays consistent regardless of how many children are visible in a given photo.
    sizing_lines = [date_line] + [age_string(name, 10, 10) for name, _ in children]
    longest_line = max(sizing_lines, key=len)
    lo, hi = 6, max(img_h, img_w)
    font = load_font(lo)
    for _ in range(20):  # 20 iterations is plenty for binary search
        mid = (lo + hi) // 2
        candidate = load_font(mid)
        # Measure longest line width
        try:
            bbox = candidate.getbbox(longest_line)
            line_w = bbox[2] - bbox[0]
        except AttributeError:
            # PIL default font
            line_w = len(longest_line) * mid // 2
        if line_w < target_text_width:
            lo = mid
            font = candidate
        else:
            hi = mid
        if hi - lo <= 1:
            break

    # Measure all lines with chosen font
    line_sizes = []
    for line in all_lines:
        try:
            bbox = font.getbbox(line)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
        except AttributeError:
            lw = len(line) * 10
            lh = 16
        line_sizes.append((lw, lh))

    line_height = max(h for _, h in line_sizes)
    line_spacing = int(line_height * 0.5)
    total_text_h = line_height * len(all_lines) + line_spacing * (len(all_lines) - 1)
    max_line_w = max(w for w, _ in line_sizes)

    margin = int(img_w * 0.01)  # 1% margin from edges

    # Semi-transparent background rectangle
    pad = int(line_height * 0.2)
    rect_x1 = img_w - max_line_w - margin - pad * 2
    rect_y1 = img_h - total_text_h - margin - pad * 2
    rect_x2 = img_w - margin
    rect_y2 = img_h - margin

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle(
        [rect_x1, rect_y1, rect_x2, rect_y2],
        fill=(0, 0, 0, 160),
    )

    # Draw each line right-aligned inside the rectangle
    y = rect_y1 + pad
    for i, (line, (lw, lh)) in enumerate(zip(all_lines, line_sizes)):
        x = rect_x2 - pad - lw
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height + line_spacing

    # Composite and convert back
    stamped = Image.alpha_composite(img, overlay).convert("RGB")

    if dry_run:
        print(f"  [dry-run] Would write: {output_path}")
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stamped.save(output_path, quality=95, subsampling=0)
    except Exception as e:
        print(f"  Error saving {output_path}: {e}", file=sys.stderr)
        return False

    return True


def process_folder(
    source: Path,
    output: Path,
    children: list[tuple[str, date]],
    dry_run: bool,
    overwrite: bool,
) -> None:
    """Recursively walk source folder and stamp all supported images."""
    total = processed = skipped = errors = 0

    for image_path in sorted(source.rglob("*")):
        if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        total += 1

        # Mirror directory structure in output
        relative = image_path.relative_to(source)
        out_path = output / relative

        if not overwrite and out_path.exists():
            print(f"  Skipping {relative}: output already exists (use --overwrite).")
            skipped += 1
            continue

        print(f"Processing: {relative}")
        success = stamp_image(image_path, out_path, children, dry_run)
        if success:
            processed += 1
        else:
            errors += 1

    print(f"\nDone. {total} image(s) found, {processed} stamped, "
          f"{skipped} skipped, {errors} error(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stamp date-taken (and child ages) onto images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Source folder containing images (searched recursively).",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output folder for stamped images. Defaults to '<source>_stamped'.",
    )
    parser.add_argument(
        "--children", "-c",
        nargs="+",
        metavar="NAME=YYYY-MM-DD",
        default=[],
        help=(
            "One or more children in the format Name=YYYY-MM-DD. "
            "Their age at the time of each photo will be printed under the date. "
            "Example: --children Wesley=2024-04-01 Hazel=2022-01-15"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview which files would be processed without writing anything.",
    )

    args = parser.parse_args()

    source: Path = args.source.resolve()
    if not source.is_dir():
        sys.exit(f"Error: source folder '{source}' does not exist or is not a directory.")

    output: Path = args.output.resolve() if args.output else source.parent / (source.name + "_stamped")

    children = parse_children(args.children)
    if children:
        print("Children:")
        for name, dob in children:
            print(f"  {name} — born {dob}")
    print(f"Source : {source}")
    print(f"Output : {output}")
    if args.dry_run:
        print("Mode   : dry-run (no files will be written)")
    print()

    process_folder(source, output, children, dry_run=args.dry_run, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
