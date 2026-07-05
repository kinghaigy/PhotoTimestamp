# 📷 Photo Timestamp

Automatically stamps the **date a photo was taken** onto the bottom-right corner of every image in a folder — including subfolders. Optionally, it also prints the **name and age** of each of your children at the time the photo was taken.

Great for printing photo books or sharing memories where the date and kids' ages tell the story at a glance.

This was fully vibed in a morning with Claude. We were sick of the online photo printers messing up the ordering of images post-printing from how they were supplied and needed a way of organising images into the ages the kids are for easy scrap booking. 

---

## Example output

```
5/7/2026
Tom - 4 years, 9 months
Dick - 2 years, 10 months
Harry - 7 months
```

The text appears in the bottom-right corner of each photo on a semi-transparent dark background, sized to be readable at 33% of the image short edge. This keeps text size visually consistent between portrait and landscape photos. The font size stays consistent across all photos regardless of how many children were born at the time.

---

## Quick start

> These instructions are written for **Windows**. If you're on a Mac or Linux, see [Mac / Linux](#mac--linux) below.

### Step 1 — Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow **Download Python** button
3. Run the installer
4. **Important:** on the first screen of the installer, tick the box that says **"Add Python to PATH"** before clicking Install

### Step 2 — Download this project

1. On this GitHub page, click the green **`<> Code`** button near the top right
2. Click **Download ZIP** from the dropdown menu
3. Once downloaded, find the ZIP file (probably in your Downloads folder)
4. Right-click the ZIP file and choose **Extract All…**
5. Choose a location that's easy to find, like your **Desktop** or **Documents** folder, and click **Extract**
6. Open the extracted folder — it will be called something like `PhotoTimestamp-main`

### Step 3 — Set up your children's names and birthdays

Open the `Run Windows.bat` file in Notepad (right-click → Open with → Notepad).

Find this line near the top:

```
SET CHILDREN=Tom=2021-04-29 Dick=2023-08-09 Harry=2025-01-13
```

Replace the names and dates with your own children's details. The date format is **YYYY-MM-DD** (year-month-day). Just list them one after another separated by a space — no extra words needed.

For example, for one child named Sophie born on 3 March 2020:
```
SET CHILDREN=Sophie=2020-03-03
```

For two children:
```
SET CHILDREN=Sophie=2020-03-03 Jack=2022-11-18
```

Save and close Notepad when you're done.

### Step 4 — Add your photos

Create a folder called `photos` inside the project folder (it may already exist). Copy all the photos you want to stamp into that folder. You can organise them into subfolders — the script will find them all.

### Step 5 — Run it!

Double-click `Run Windows.bat`.

A black window will appear showing progress. When it says **Finished!**, press Enter to close it.

Your stamped photos will be in a new folder called `photos_stamped`, right next to the `photos` folder. Your original photos are never changed.

> **First run only:** The script will install the tools it needs automatically. This takes about 30 seconds and only happens once.

---

## Mac / Linux

### Prerequisites

Make sure Python 3 is installed. On most Macs it comes pre-installed. You can check by opening Terminal and typing:
```bash
python3 --version
```

If you see a version number, you're good. If not, download it from [python.org](https://www.python.org/downloads/).

### Setup

Open Terminal, navigate to the project folder, and run:

```bash
bash "Run Linux and Mac.sh"
```

That's it. On first run it sets up the Python environment and installs everything needed automatically.

---

## Folder structure

```
PhotoTimestamp/
├── photos/               ← Put your photos here (subfolders are fine)
│   ├── 2022/
│   │   └── birthday.jpg
│   └── holiday.jpg
├── photos_stamped/       ← Stamped output appears here (created automatically)
├── photo_timestamp.py    ← The main script
├── Run Windows.bat       ← Double-click to run on Windows
├── Run Linux and Mac.sh  ← Run on Mac/Linux
└── requirements.txt      ← Python dependencies (installed automatically)
```

---

## Advanced usage

The script can also be run directly from the command line for more control.

```bash
# Basic — just date
python photo_timestamp.py ./photos

# Custom output folder
python photo_timestamp.py ./photos --output ./my_output

# With children
python photo_timestamp.py ./photos \
  --children Tom=2021-04-29 Dick=2023-08-09 Harry=2025-01-13

# Re-process files that were already stamped
python photo_timestamp.py ./photos --children Tom=2021-04-29 --overwrite

# Preview without writing any files
python photo_timestamp.py ./photos --children Tom=2021-04-29 --dry-run
```

### All options

| Option | Description |
|---|---|
| `source` | Folder containing your photos (required) |
| `--output`, `-o` | Where to save stamped images (default: `<source>_stamped`) |
| `--children`, `-c` | One or more children as `Name=YYYY-MM-DD` |
| `--overwrite` | Re-process images that already exist in the output folder |
| `--dry-run` | Show what would be processed without writing anything |

---

## Supported image formats

`.jpg` · `.jpeg` · `.png` · `.tiff` · `.tif` · `.webp`

The date is read from the photo's **EXIF metadata** — the hidden information your camera or phone embeds in every photo. If a photo has no EXIF date (e.g. screenshots or edited files), it will be skipped.

---

## Notes

- **Original photos are never modified.** All output goes to a separate folder.
- Children who weren't born yet at the time a photo was taken are automatically excluded from that photo.
- The font size is consistent across all photos in a batch, sized to the full set of children you've configured.
- On first run, a `.venv` folder is created next to the script. This is normal — it contains the Python tools the script needs.

---

## Requirements

- Python 3.10 or later
- [Pillow](https://python-pillow.org/) — image processing
- [piexif](https://github.com/hMatoba/Piexif) — EXIF date reading

Both are installed automatically by `Run Windows.bat` / `Run Linux and Mac.sh`.
