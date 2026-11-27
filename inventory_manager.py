#!/usr/bin/env python3
"""Manage Reboot Archive inventory and publish active listings to the static site."""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT / "inventory"
CATALOG = INVENTORY / "catalog.json"
SEQUENCE = INVENTORY / "sequence.json"
COLLECTIONS = ROOT / "collections.html"
ARCHIVE = ROOT / "archive.html"
ID_RE = re.compile(r"^RA(\d+)$")
SERIES = ["iPhone", "iPad", "Mac", "iPod", "other"]
CATEGORIES = ["Desktop", "Portable", "Music", "Accessories", "Other"]
STATUSES = ["available", "sold"]
FIELDS = [
    "Title",
    "Product ID",
    "Category",
    "Device Series",
    "Device Model",
    "Description",
    "Condition",
    "Cover image",
    "Additional images",
    "Storage (optional value)",
    "RAM (optional value)",
    "Price (in GBP)",
    "eBay link",
    "Condition report PDF (optional value)",
    "Status",
]


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_json(path: Path, data) -> None:
    atomic_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read {path}: {error}") from error


def ensure_setup() -> None:
    INVENTORY.mkdir(parents=True, exist_ok=True)
    if not CATALOG.exists():
        write_json(CATALOG, {"Listings": []})
    if not SEQUENCE.exists():
        write_json(SEQUENCE, {"Last issued": 0})
    if not COLLECTIONS.exists():
        raise RuntimeError(f"Website collections page not found: {COLLECTIONS}")
    if not ARCHIVE.exists():
        raise RuntimeError(f"Website archive page not found: {ARCHIVE}")
    source = COLLECTIONS.read_text(encoding="utf-8")
    if "<!-- INVENTORY:START -->" not in source or "<!-- INVENTORY:END -->" not in source:
        raise RuntimeError(
            "Collections page is missing inventory markers; refusing to overwrite its product grid."
        )
    archive_source = ARCHIVE.read_text(encoding="utf-8")
    if (
        "<!-- ARCHIVE:START -->" not in archive_source
        or "<!-- ARCHIVE:END -->" not in archive_source
    ):
        raise RuntimeError(
            "Archive page is missing archive markers; refusing to overwrite its listing grid."
        )
    if ".visual img{" not in source:
        source = source.replace(
            ".visual svg{",
            ".visual img{width:72%;height:78%;object-fit:contain;filter:drop-shadow(0 12px 10px #35352b20);transition:transform .35s}.card:hover .visual img{transform:translateY(-5px)}.visual svg{",
            1,
        )
        atomic_text(COLLECTIONS, source)
    rebuild_catalog_and_collection()


def listing_dirs() -> list[Path]:
    if not INVENTORY.exists():
        return []
    return sorted(
        (path for path in INVENTORY.iterdir() if path.is_dir() and ID_RE.fullmatch(path.name)),
        key=lambda path: int(ID_RE.fullmatch(path.name).group(1)),
    )


def all_listings() -> list[dict]:
    items = []
    for folder in listing_dirs():
        data = read_json(folder / "listing.json")
        if isinstance(data, dict):
            items.append(data)
    return items


def next_product_id() -> str:
    sequence = read_json(SEQUENCE, {"Last issued": 0}) or {"Last issued": 0}
    last = int(sequence.get("Last issued", 0))
    for folder in listing_dirs():
        match = ID_RE.fullmatch(folder.name)
        if match:
            last = max(last, int(match.group(1)))
    next_number = last + 1
    write_json(SEQUENCE, {"Last issued": next_number})
    return f"RA{next_number:04d}"


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def relative_image(folder: Path, filename: str, from_collection: bool = False) -> str:
    if not filename:
        return ""
    safe_name = Path(filename).name
    relative = f"inventory/{folder.name}/{safe_name}"
    return quote(relative, safe="/") if from_collection else quote(safe_name)


def money(value) -> str:
    if value in (None, ""):
        return "Price on eBay"
    try:
        return f"£{Decimal(str(value)):,.2f}"
    except InvalidOperation:
        return f"£{value}"


# Legacy embedded-template implementation removed.


def product_page(data: dict, folder: Path) -> str:
    """Build a listing page that uses the shared external listing stylesheet."""
    product_id = esc(data["Product ID"])
    title = esc(data.get("Title") or "Untitled listing")
    category = esc(data.get("Category", ""))
    series = esc(data.get("Device Series", ""))
    status = str(data.get("Status", "available")).lower()
    archived = bool(data.get("Archived", False))
    sold_date = esc(data.get("Date sold", ""))
    description = str(data.get("Description") or "")
    ebay_url = esc(data.get("eBay link", ""))
    report_name = Path(str(data.get("Condition report PDF (optional value)") or "")).name
    report_link = (
        f"""          <p class="report-link">
            <a
              class="report-link__anchor"
              href="{quote(report_name)}"
              target="_blank"
              rel="noopener noreferrer"
            >
              View condition, testing &amp; repairs report (PDF) &#8599;&#65038;
            </a>
          </p>"""
        if report_name and (folder / report_name).is_file()
        else ""
    )

    cover = data.get("Cover image") or ""
    images = [cover] if cover else []
    images.extend(
        image for image in data.get("Additional images", []) if image and image not in images
    )
    gallery = "\n".join(
        f'          <img src="{relative_image(folder, image)}" alt="{title}" loading="lazy" />'
        for image in images
    )
    if not gallery:
        gallery = (
            '          <div class="photo-empty">Photography for this piece is being prepared.</div>'
        )

    description_html = (
        "\n".join(
            f"            <p>{esc(paragraph)}</p>"
            for paragraph in re.split(r"\n\s*\n", description.strip())
            if paragraph.strip()
        )
        or "<p>Description coming soon.</p>"
    )
    specs = []
    for label, key in (
        ("Series", "Device Series"),
        ("Model", "Device Model"),
        ("Condition", "Condition"),
        ("Storage", "Storage (optional value)"),
        ("Memory", "RAM (optional value)"),
    ):
        if (value := data.get(key)) not in (None, ""):
            specs.append(
                f"""            <div>
              <dt>{esc(label)}</dt>
              <dd>{esc(value)}</dd>
            </div>"""
            )

    sold_badge = '          <span class="sold">Sold</span>' if status == "sold" or archived else ""
    sold_note = (
        f'          <p class="availability">Sold {sold_date}</p>' if archived and sold_date else ""
    )
    price = data.get("Price (in GBP)")
    price_html = (
        f'          <p class="price">{money(price)}</p>'
        if price not in (None, "")
        else '          <p class="price">Price on eBay</p>'
    )
    ebay_button = (
        '          <p class="availability">This listing has been archived.</p>'
        if archived
        else (
            f"""          <a class="ebay-button" href="{ebay_url}" target="_blank" rel="noopener noreferrer">
            View on eBay <span aria-hidden="true">&#8599;&#65038;</span>
          </a>"""
            if ebay_url
            else '          <p class="availability">eBay link not added yet.</p>'
        )
    )
    back_page = "archive.html" if archived else "collections.html"
    back_label = "archive" if archived else "collection"

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#f5f3ee" />
    <meta name="description" content="{esc(description[:240])}" />
    <link rel="icon" type="image/png" href="../../favicon-collapsed.png" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="../../assets/css/listing.css" />
    <link rel="stylesheet" href="../../navigation.css" />
    <script src="../../navigation.js" defer></script>
    <title>{title} — Reboot Archive</title>
  </head>
  <body>
    <div class="announcement">A second life for the objects that changed everything</div>
    <header class="nav">
      <a class="brand" href="../../index.html">
        <img src="../../favicon-collapsed.png" alt="" />
        <span><strong>Reboot Archive</strong><span>Vintage Apple, reimagined</span></span>
      </a>
      <nav class="nav-links" aria-label="Main navigation">
        <a href="../../collections.html">The collection</a>
        <a href="../../story.html">Our story</a>
        <a href="../../explore.html">Explore</a>
      </nav>
    </header>
    <main>
      <a class="crumb" href="../../{back_page}">← Back to the {back_label}</a>
      <div class="layout">
        <div class="gallery">
{gallery}
        </div>
        <section>
          <div class="eyebrow">{category} · {series}</div>
          <h1>{title}</h1>
          <div class="id">PRODUCT {product_id}</div>
{sold_badge}
{sold_note}
{price_html}
          <dl>
{chr(10).join(specs)}
          </dl>
          <div class="description">
{description_html}
          </div>
{report_link}
{ebay_button}
        </section>
      </div>
    </main>
    <footer>Reboot Archive · Objects with a past, ready for what’s next.</footer>
  </body>
</html>
"""


def collection_card(data: dict) -> str:
    product_id = str(data["Product ID"])
    title = esc(data.get("Title") or "Untitled listing")
    category = str(data.get("Category") or "Other").lower()
    if category not in {"desktop", "portable", "music", "accessories", "other"}:
        category = "other"
    path = INVENTORY / product_id
    cover = data.get("Cover image") or ""
    if cover and (path / Path(cover).name).is_file():
        media = f'<img src="{relative_image(path, cover, from_collection=True)}" alt="{title}" loading="lazy">'
    else:
        media = '<span class="catalog-empty">Reboot<br>Archive</span>'
    status = str(data.get("Status", "available")).lower()
    badge = (
        '<span class="tag">Sold</span>'
        if status == "sold"
        else '<span class="tag">Curated vintage</span>'
    )
    price = money(data.get("Price (in GBP)"))
    model = " · ".join(
        part for part in (data.get("Device Series", ""), data.get("Device Model", "")) if part
    )
    subline = esc(model or data.get("Condition", ""))
    return f'<a class="card" data-product-id="{esc(product_id)}" data-category="{esc(category)}" href="inventory/{quote(product_id)}/listing.html"><div class="visual">{badge}{media}</div><div class="details"><div>{title}<small>{subline}</small></div><span class="price">{esc(price)}</span></div></a>'


def archive_card(data: dict) -> str:
    card = collection_card(data)
    sold_date = esc(data.get("Date sold", "Date not recorded"))
    card = card.replace('<span class="tag">Curated vintage</span>', '<span class="tag">Sold</span>')
    return card.replace(
        "</div></a>", f'<small class="sold-date">Sold {sold_date}</small></div></a>'
    )


def rebuild_catalog_and_collection() -> None:
    all_items = all_listings()
    active = [
        item for item in all_items if item.get("Active", False) and not item.get("Archived", False)
    ]
    archived = sorted(
        (item for item in all_items if item.get("Archived", False)),
        key=lambda item: str(item.get("Date sold", "")),
        reverse=True,
    )
    entries = []
    for item in all_items:
        product_id = str(item.get("Product ID", ""))
        if not ID_RE.fullmatch(product_id):
            continue
        entries.append(
            {
                "Product ID": product_id,
                "Catalog URL": f"inventory/{product_id}/listing.html",
                "Title": item.get("Title", ""),
                "Category": item.get("Category", "Other"),
                "Device Series": item.get("Device Series", "other"),
                "Device Model": item.get("Device Model", ""),
                "Price (in GBP)": item.get("Price (in GBP)"),
                "Status": item.get("Status", "available"),
            }
        )
    write_json(CATALOG, {"Listings": entries})

    source = COLLECTIONS.read_text(encoding="utf-8")
    start_marker, end_marker = "<!-- INVENTORY:START -->", "<!-- INVENTORY:END -->"
    start = source.index(start_marker) + len(start_marker)
    end = source.index(end_marker, start)
    cards = "\n" + "\n".join(collection_card(item) for item in active) + "\n" if active else "\n"
    source = source[:start] + cards + source[end:]
    atomic_text(COLLECTIONS, source)

    archive_source = ARCHIVE.read_text(encoding="utf-8")
    start_marker, end_marker = "<!-- ARCHIVE:START -->", "<!-- ARCHIVE:END -->"
    start = archive_source.index(start_marker) + len(start_marker)
    end = archive_source.index(end_marker, start)
    cards = (
        "\n" + "\n".join(archive_card(item) for item in archived) + "\n"
        if archived
        else '\n<div class="empty">No past listings in the archive just yet.</div>\n'
    )
    archive_source = archive_source[:start] + cards + archive_source[end:]
    atomic_text(ARCHIVE, archive_source)


def new_record(product_id: str, active: bool) -> dict:
    return {
        "Title": "",
        "Product ID": product_id,
        "Category": "Other",
        "Device Series": "other",
        "Device Model": "",
        "Description": "",
        "Condition": "",
        "Cover image": "",
        "Additional images": [],
        "Storage (optional value)": None,
        "RAM (optional value)": None,
        "Price (in GBP)": None,
        "eBay link": "",
        "Condition report PDF (optional value)": "",
        "Status": "available",
        "Active": active,
    }


def save_listing(data: dict) -> None:
    product_id = str(data["Product ID"])
    if data.get("Archived"):
        data["Status"] = "sold"
        data["Active"] = False
    folder = INVENTORY / product_id
    folder.mkdir(parents=True, exist_ok=True)
    data["Description"] = str(data.get("Description") or "")
    write_json(folder / "listing.json", data)
    atomic_text(folder / "description.txt", data["Description"])
    atomic_text(folder / "listing.html", product_page(data, folder))
    rebuild_catalog_and_collection()


def choose(label: str, options: list[str], current: str | None = None) -> str:
    print(f"{label}:")
    for index, option in enumerate(options, 1):
        mark = " (current)" if option == current else ""
        print(f"  {index}. {option}{mark}")
    while True:
        answer = input(
            "Choose a number" + (" (Enter keeps current)" if current else "") + ": "
        ).strip()
        if not answer and current:
            return current
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print("Please choose one of the listed numbers.")


def ask_text(label: str, current: str = "", required: bool = False) -> str:
    while True:
        suffix = f" [{current}]" if current else ""
        answer = input(f"{label}{suffix}: ").strip()
        value = answer if answer else current
        if not required or value:
            return value
        print("This field is required.")


def ask_multiline(label: str, current: str = "") -> str:
    if current:
        keep = input(f"{label} — press Enter to keep it, or type R to replace: ").strip().lower()
        if keep != "r":
            return current
    print(f"{label}. Enter one or more lines; finish with a line containing only a period (.).")
    lines = []
    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def ask_price(current=None):
    while True:
        suffix = f" [{current}]" if current is not None else ""
        value = input(f"Price in GBP (number only){suffix}: ").strip()
        if not value:
            return current
        if value == "-":
            return None
        try:
            amount = Decimal(value.replace("£", "").replace(",", ""))
            if amount < 0:
                raise InvalidOperation
            return float(amount.quantize(Decimal("0.01")))
        except InvalidOperation:
            print("Enter a non-negative amount, or - to clear the price.")


def copy_image(source_text: str, folder: Path, target_name: str) -> str:
    source = Path(source_text).expanduser()
    if not source.is_file():
        raise ValueError(f"Image file not found: {source}")
    suffix = source.suffix.lower() or ".jpg"
    filename = target_name + suffix
    shutil.copy2(source, folder / filename)
    return filename


IMAGE_FILE_TYPES = ["public.image"]
PDF_FILE_TYPES = ["com.adobe.pdf"]


def choose_files(title: str, file_types: list[str], multiple: bool = False) -> list[str]:
    """Open macOS's native picker, without loading Tk into this Python process.

    ``choose file`` is backed by macOS Cocoa, rather than Tk's Tcl/Tk bridge.  A
    cancelled dialog returns an empty list.  The text prompt is kept as a
    dependable fallback for non-macOS systems or when GUI automation is
    unavailable (for example over SSH).
    """
    if sys.platform == "darwin":
        apple_types = ", ".join(f'"{file_type}"' for file_type in file_types)
        chooser = (
            f"choose file with prompt {json.dumps(title)} of type {{{apple_types}}} with multiple selections allowed"
            if multiple
            else f"{{choose file with prompt {json.dumps(title)} of type {{{apple_types}}}}}"
        )
        script = f"""try
    set selectedFiles to {chooser}
    set selectedPaths to ""
    repeat with selectedFile in selectedFiles
        set selectedPaths to selectedPaths & POSIX path of selectedFile & linefeed
    end repeat
    return selectedPaths
on error number -128
    return ""
end try"""
        try:
            result = subprocess.run(
                ["osascript", "-l", "AppleScript", "-e", script],
                check=True,
                capture_output=True,
                text=True,
            )
            return [path for path in result.stdout.splitlines() if path]
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"Could not open the macOS file picker ({error}); using a typed path instead.")

    plural = "s, one per line" if multiple else ""
    print(f"{title}. Paste a file path{plural}, then press Enter on a blank line to finish.")
    paths = []
    while True:
        path = input("File path (blank to finish): ").strip()
        if not path:
            return paths
        paths.append(path)
        if not multiple:
            return paths


def copy_report(source_text: str, folder: Path) -> str:
    source = Path(source_text).expanduser()
    if not source.is_file():
        raise ValueError(f"PDF file not found: {source}")
    if source.suffix.lower() != ".pdf":
        raise ValueError("The condition report must be a PDF file.")
    target = folder / "condition-report.pdf"
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target.name


def choose_listing_images() -> list[str]:
    """Collect any number of listing photographs in one or more picker rounds."""
    print(
        "Listing photos: choose images that will appear in the product listing. These are not the device report PDF."
    )
    paths: list[str] = []
    while True:
        selected = choose_files(
            "Select one or more photos for this product listing",
            IMAGE_FILE_TYPES,
            multiple=True,
        )
        paths.extend(path for path in selected if path not in paths)
        if not selected:
            print("No more listing photos selected.")
            return paths
        more = input("Add more listing photos? [Y/n]: ").strip().lower()
        if more not in {"", "y", "yes"}:
            return paths


def ask_images(data: dict, folder: Path, editing: bool) -> None:
    current = data.get("Cover image", "")
    if editing:
        answer = (
            input(
                f"Cover image [{current or 'none'}]: Enter keeps current, C chooses a file, - clears: "
            )
            .strip()
            .lower()
        )
        if answer == "-":
            data["Cover image"] = ""
            path = ""
        elif answer in {"c", "choose", "y", "yes"}:
            print(
                "Cover image: choose the main photograph used on the collection card and first in the listing gallery."
            )
            paths = choose_files(
                "Select the cover image for this product listing", IMAGE_FILE_TYPES
            )
            path = paths[0] if paths else ""
        else:
            path = ""
    else:
        print(
            "Cover image: choose the main photograph used on the collection card and first in the listing gallery."
        )
        paths = choose_files("Select the cover image for this product listing", IMAGE_FILE_TYPES)
        path = paths[0] if paths else ""
    if path:
        try:
            data["Cover image"] = copy_image(path, folder, "cover")
        except ValueError as error:
            print(error, "Keeping the existing cover image.")
    elif not editing and not current:
        data["Cover image"] = ""

    if editing:
        current_images = data.get("Additional images", [])
        action = (
            input(
                "Additional listing photos: Enter keeps current, - clears, or C chooses photos (repeat as needed): "
            )
            .strip()
            .lower()
        )
        if not action:
            return
        if action == "-":
            data["Additional images"] = []
            return
        if action not in {"c", "choose", "y", "yes"}:
            return
        paths = choose_listing_images()
    else:
        current_images = []
        paths = choose_listing_images()
    copied = []
    for index, source in enumerate(paths, 1):
        try:
            copied.append(copy_image(source, folder, f"image-{index:02d}"))
        except ValueError as error:
            print(error)
    data["Additional images"] = copied if paths else current_images


def complete_assisted(data: dict, folder: Path, editing: bool = False) -> dict:
    data["Title"] = ask_text("Title", data.get("Title", ""), required=not editing)
    data["Category"] = choose("Category", CATEGORIES, data.get("Category") if editing else None)
    data["Device Series"] = choose(
        "Device Series", SERIES, data.get("Device Series") if editing else None
    )
    data["Device Model"] = ask_text(
        "Device Model", data.get("Device Model", ""), required=not editing
    )
    data["Description"] = ask_multiline("Description", data.get("Description", ""))
    data["Condition"] = ask_text("Condition", data.get("Condition", ""), required=not editing)
    data["Storage (optional value)"] = (
        ask_text("Storage (optional; - clears)", str(data.get("Storage (optional value)") or ""))
        or None
    )
    data["RAM (optional value)"] = (
        ask_text("RAM (optional; - clears)", str(data.get("RAM (optional value)") or "")) or None
    )
    if data["Storage (optional value)"] == "-":
        data["Storage (optional value)"] = None
    if data["RAM (optional value)"] == "-":
        data["RAM (optional value)"] = None
    data["Price (in GBP)"] = ask_price(data.get("Price (in GBP)"))
    data["eBay link"] = ask_text("eBay link", data.get("eBay link", ""), required=not editing)
    if editing:
        report_action = (
            input(
                "Device report PDF (condition, testing and repairs): Enter keeps current, C chooses the PDF, - clears: "
            )
            .strip()
            .lower()
        )
        if report_action == "-":
            data["Condition report PDF (optional value)"] = ""
            report_path = ""
        elif report_action in {"c", "choose", "y", "yes"}:
            print(
                "Device report: choose the condition, testing and repairs PDF. Do not choose listing photos here."
            )
            chosen = choose_files("Select the device report PDF", PDF_FILE_TYPES)
            report_path = chosen[0] if chosen else ""
        else:
            report_path = ""
    else:
        print(
            "Device report: choose the optional condition, testing and repairs PDF. Do not choose listing photos here."
        )
        chosen = choose_files("Select the optional device report PDF", PDF_FILE_TYPES)
        report_path = chosen[0] if chosen else ""
    if report_path:
        try:
            data["Condition report PDF (optional value)"] = copy_report(report_path, folder)
        except ValueError as error:
            print(error, "Skipping the PDF report.")
    data["Status"] = choose("Status", STATUSES, data.get("Status") if editing else None)
    ask_images(data, folder, editing)
    if not editing:
        complete = all(data.get(key) for key in ("Title", "Device Model", "Condition", "eBay link"))
        data["Active"] = bool(complete)
        if not complete:
            print("Listing saved as inactive because one or more required fields are blank.")
    return data


def create_listing(assisted: bool) -> None:
    product_id = next_product_id()
    folder = INVENTORY / product_id
    folder.mkdir(parents=True, exist_ok=False)
    data = new_record(product_id, active=False)
    if assisted:
        data = complete_assisted(data, folder)
    save_listing(data)
    print(f"Saved {product_id} in {folder}")


def select_listing() -> dict | None:
    items = all_listings()
    if not items:
        print("There are no listings yet.")
        return None
    print("Listings:")
    for index, item in enumerate(items, 1):
        visibility = "active" if item.get("Active", False) else "inactive"
        print(
            f"  {index}. {item.get('Product ID')} — {item.get('Title') or 'Untitled listing'} ({visibility}, {item.get('Status', 'available')})"
        )
    while True:
        answer = input("Choose a listing number, or Q to cancel: ").strip().lower()
        if answer == "q":
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(items):
            return items[int(answer) - 1]
        print("Please choose one of the listed numbers, or Q.")


def edit_listing() -> None:
    current = select_listing()
    if not current:
        return
    folder = INVENTORY / current["Product ID"]
    updated = complete_assisted(current.copy(), folder, editing=True)
    visibility = (
        input(
            f"Visible in the website catalog? [Y/n, currently {'yes' if updated.get('Active') else 'no'}]: "
        )
        .strip()
        .lower()
    )
    if visibility in {"y", "yes"}:
        updated["Active"] = True
    elif visibility in {"n", "no"}:
        updated["Active"] = False
    save_listing(updated)
    print(f"Updated {updated['Product ID']}.")


def set_visibility(active: bool) -> None:
    current = select_listing()
    if not current:
        return
    if active and current.get("Archived"):
        print(
            f"{current['Product ID']} is archived and cannot be reactivated in the current listing catalog."
        )
        return
    if bool(current.get("Active")) == active:
        print(f"{current['Product ID']} is already {'active' if active else 'inactive'}.")
        return
    current["Active"] = active
    save_listing(current)
    print(
        f"{current['Product ID']} is now {'visible in' if active else 'removed from'} the website catalog."
    )


def archive_listing() -> None:
    current = select_listing()
    if not current:
        return
    if current.get("Archived"):
        print(f"{current['Product ID']} is already in The Archive.")
        return
    while True:
        sold_date = input("Date sold (YYYY-MM-DD): ").strip()
        try:
            from datetime import date

            date.fromisoformat(sold_date)
            break
        except ValueError:
            print("Enter a valid date in YYYY-MM-DD format.")
    current["Status"] = "sold"
    current["Active"] = False
    current["Archived"] = True
    current["Date sold"] = sold_date
    folder = INVENTORY / current["Product ID"]
    save_listing(current)
    print(f"Archived {current['Product ID']} (sold {sold_date}) in {folder}.")


def regenerate_listing() -> None:
    current = select_listing()
    if not current:
        return
    product_id = str(current.get("Product ID", ""))
    if not ID_RE.fullmatch(product_id):
        print("Cannot regenerate: this listing has an invalid product ID.")
        return
    folder = INVENTORY / product_id
    if not folder.is_dir():
        print(f"Cannot regenerate: listing folder not found: {folder}")
        return
    data = read_json(folder / "listing.json")
    if not isinstance(data, dict):
        print(f"Cannot regenerate: listing.json is missing or invalid for {product_id}.")
        return
    changed = False
    if (
        not data.get("Condition report PDF (optional value)")
        and (folder / "condition-report.pdf").is_file()
    ):
        data["Condition report PDF (optional value)"] = "condition-report.pdf"
        changed = True
    missing_fields = [
        ("Title", "Title"),
        ("Category", "Category"),
        ("Device Series", "Device Series"),
        ("Device Model", "Device Model"),
        ("Description", "Description"),
        ("Condition", "Condition"),
        ("Storage (optional value)", "Storage (optional value)"),
        ("RAM (optional value)", "RAM (optional value)"),
        ("Price (in GBP)", "Price (in GBP)"),
        ("eBay link", "eBay link"),
        ("Cover image", "Cover image file path"),
        ("Condition report PDF (optional value)", "Condition/testing/repairs PDF path"),
    ]
    missing = [(key, label) for key, label in missing_fields if data.get(key) in (None, "")]
    if missing:
        print(
            "Some listing values are blank. Enter a value when prompted, or press Enter to leave it out."
        )
        for key, label in missing:
            if key == "Cover image":
                print("Cover image: choose the main photograph for the product listing.")
                selected = choose_files(
                    "Select the cover image for this product listing", IMAGE_FILE_TYPES
                )
                answer = selected[0] if selected else ""
            elif key == "Condition report PDF (optional value)":
                print(
                    "Device report: choose the condition, testing and repairs PDF, not a listing photograph."
                )
                selected = choose_files("Select the device report PDF", PDF_FILE_TYPES)
                answer = selected[0] if selected else ""
            else:
                answer = input(f"{label}: ").strip()
            if not answer:
                continue
            if key == "Price (in GBP)":
                try:
                    amount = Decimal(answer.replace("£", "").replace(",", ""))
                    if amount < 0:
                        raise InvalidOperation
                    data[key] = float(amount.quantize(Decimal("0.01")))
                except InvalidOperation:
                    print("Invalid price; leaving it blank.")
                    continue
            elif key == "Cover image":
                try:
                    data[key] = copy_image(answer, folder, "cover")
                except ValueError as error:
                    print(error, "Leaving the cover image blank.")
                    continue
            elif key == "Condition report PDF (optional value)":
                try:
                    data[key] = copy_report(answer, folder)
                except ValueError as error:
                    print(error, "Leaving the PDF report blank.")
                    continue
            else:
                data[key] = answer
            changed = True
    if changed:
        data["Product ID"] = product_id
        write_json(folder / "listing.json", data)
        atomic_text(folder / "description.txt", str(data.get("Description") or ""))
    atomic_text(folder / "listing.html", product_page(data, folder))
    rebuild_catalog_and_collection()
    print(f"Regenerated {product_id} from its current listing.json.")


def print_menu() -> None:
    print("\nReboot Archive · Inventory Manager")
    print("1. Create a blank listing")
    print("2. Create a listing with prompts")
    print("3. Edit a listing")
    print("4. Deactivate a listing")
    print("5. Reactivate a listing")
    print("6. List inventory")
    print("7. Archive a sold listing")
    print("8. Regenerate a listing from JSON")
    print("9. Exit")


def main() -> int:
    try:
        ensure_setup()
        while True:
            print_menu()
            choice = input("Select an option: ").strip()
            if choice == "1":
                create_listing(assisted=False)
            elif choice == "2":
                create_listing(assisted=True)
            elif choice == "3":
                edit_listing()
            elif choice == "4":
                set_visibility(active=False)
            elif choice == "5":
                set_visibility(active=True)
            elif choice == "6":
                select_listing()
            elif choice == "7":
                archive_listing()
            elif choice == "8":
                regenerate_listing()
            elif choice == "9":
                return 0
            else:
                print("Choose a number from 1 to 9.")
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Inventory manager: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
