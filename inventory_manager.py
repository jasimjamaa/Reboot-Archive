#!/usr/bin/env python3
"""Manage Reboot Archive inventory and publish active listings to the static site."""

from __future__ import annotations

import html
import json
import re
import shutil
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
    "Status",
]


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
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
    source = COLLECTIONS.read_text(encoding="utf-8")
    if "<!-- INVENTORY:START -->" not in source or "<!-- INVENTORY:END -->" not in source:
        raise RuntimeError("Collections page is missing inventory markers; refusing to overwrite its product grid.")
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


def product_page(data: dict, folder: Path) -> str:
    product_id = esc(data["Product ID"])
    title = esc(data.get("Title") or "Untitled listing")
    category = esc(data.get("Category", ""))
    series = esc(data.get("Device Series", ""))
    model = esc(data.get("Device Model", ""))
    condition = esc(data.get("Condition", ""))
    status = str(data.get("Status", "available")).lower()
    description = str(data.get("Description") or "")
    ebay_url = esc(data.get("eBay link", ""))
    cover = data.get("Cover image") or ""
    images = [cover] if cover else []
    images.extend(image for image in data.get("Additional images", []) if image and image not in images)
    gallery = "".join(
        f'<img src="{relative_image(folder, image)}" alt="{title}" loading="lazy">' for image in images
    )
    if not gallery:
        gallery = '<div class="photo-empty">Photography for this piece is being prepared.</div>'
    description_html = "".join(
        f"<p>{esc(paragraph)}</p>" for paragraph in re.split(r"\n\s*\n", description.strip()) if paragraph.strip()
    ) or "<p>Description coming soon.</p>"
    specs = []
    for label, key in (("Series", "Device Series"), ("Model", "Device Model"), ("Condition", "Condition"), ("Storage", "Storage (optional value)"), ("Memory", "RAM (optional value)")):
        value = data.get(key)
        if value not in (None, ""):
            specs.append(f"<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>")
    sold_badge = '<span class="sold">Sold</span>' if status == "sold" else ""
    ebay_button = f'<a class="ebay-button" href="{ebay_url}" target="_blank" rel="noopener noreferrer">View on eBay <span aria-hidden="true">↗</span></a>' if ebay_url else '<p class="availability">eBay link not added yet.</p>'
    price_value = data.get("Price (in GBP)")
    price_html = f'<p class="price">{money(price_value)}</p>' if price_value not in (None, "") else '<p class="price">Price on eBay</p>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f5f3ee"><meta name="description" content="{esc(description[:240])}"><link rel="icon" type="image/png" href="../../favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet"><title>{title} — Reboot Archive</title>
<style>:root{{--paper:#f5f3ee;--ink:#242622;--muted:#797a73;--line:#dcd9d1;--rust:#a45e43;--serif:'Playfair Display',Georgia,serif;--sans:'DM Sans',Arial,sans-serif}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans)}}a{{color:inherit;text-decoration:none}}.announcement{{height:34px;background:#292b26;color:#f5f3ee;display:grid;place-items:center;font-size:9px;letter-spacing:.16em;text-transform:uppercase}}.nav{{height:76px;padding:0 7.2%;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}}.brand{{display:flex;align-items:center;gap:10px}}.brand img{{width:34px;height:34px;object-fit:cover;border-radius:9px}}.brand strong{{display:block;font:600 17px var(--serif)}}.brand span span{{font:9px var(--sans);letter-spacing:.16em;text-transform:uppercase;display:block;margin-top:3px;color:var(--muted)}}.nav-links{{display:flex;gap:36px;font-size:10px;text-transform:uppercase;letter-spacing:.14em}}.nav-links a:hover{{color:var(--rust)}}main{{padding:54px 7.2% 90px}}.crumb{{font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}.layout{{display:grid;grid-template-columns:1.05fr .95fr;gap:7%;margin-top:26px;align-items:start}}.gallery{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.gallery img{{width:100%;aspect-ratio:1/1;object-fit:contain;background:#e9e6df;padding:12px}}.gallery img:first-child{{grid-column:1/-1;aspect-ratio:1.12/1}}.photo-empty{{min-height:380px;grid-column:1/-1;background:#e5e4dc;display:grid;place-items:center;text-align:center;padding:24px;font:24px var(--serif);color:#858879}}.eyebrow{{font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--rust)}}h1{{font:500 clamp(36px,4vw,54px)/1.08 var(--serif);letter-spacing:-.04em;margin:14px 0}}.id{{font-size:9px;color:var(--muted);letter-spacing:.12em}}.price{{font:500 20px var(--serif);margin:20px 0}}.sold{{display:inline-block;background:#e7ded5;padding:7px 10px;font-size:8px;letter-spacing:.15em;text-transform:uppercase}}.description{{font-size:12px;line-height:1.9;color:#62645e;border-top:1px solid var(--line);padding-top:17px;margin-top:22px}}.description p{{margin:0 0 12px}}dl{{margin:22px 0;border-top:1px solid var(--line)}}dl div{{display:grid;grid-template-columns:120px 1fr;padding:11px 0;border-bottom:1px solid var(--line);font-size:10px}}dt{{color:var(--muted);text-transform:uppercase;letter-spacing:.1em}}dd{{margin:0}}.ebay-button{{display:flex;justify-content:space-between;align-items:center;margin-top:27px;padding:17px 20px;background:var(--ink);color:white;text-transform:uppercase;letter-spacing:.13em;font-size:9px;transition:.2s}}.ebay-button:hover{{background:var(--rust)}}.availability{{font-size:10px;color:var(--muted)}}.category{{font-size:9px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase}}footer{{border-top:1px solid var(--line);padding:25px 7.2%;font-size:9px;color:var(--muted)}}@media(max-width:760px){{.nav{{padding:0 5%;height:68px}}.nav-links{{gap:14px;font-size:8px}}.nav-links a:nth-child(2){{display:none}}main{{padding:36px 6% 65px}}.layout{{grid-template-columns:1fr;gap:34px}}.gallery img:first-child{{aspect-ratio:1.1/1}}.photo-empty{{min-height:280px}}}}</style></head>
<body><div class="announcement">A second life for the objects that changed everything</div><header class="nav"><a class="brand" href="../../index.html"><img src="../../favicon.png" alt=""><span><strong>Reboot Archive</strong><span>Vintage Apple, reimagined</span></span></a><nav class="nav-links" aria-label="Main navigation"><a href="../../collections.html">The collection</a><a href="../../story.html">Our story</a><a href="../../explore.html">Explore</a></nav></header>
<main><a class="crumb" href="../../collections.html">← Back to the collection</a><div class="layout"><div class="gallery">{gallery}</div><section><div class="eyebrow">{category} · {series}</div><h1>{title}</h1><div class="id">PRODUCT {product_id}</div>{sold_badge}{price_html}<dl>{''.join(specs)}</dl><div class="description">{description_html}</div>{ebay_button}</section></div></main><footer>Reboot Archive · Objects with a past, ready for what’s next.</footer></body></html>'''


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
    badge = '<span class="tag">Sold</span>' if status == "sold" else '<span class="tag">Curated vintage</span>'
    price = money(data.get("Price (in GBP)"))
    model = " · ".join(part for part in (data.get("Device Series", ""), data.get("Device Model", "")) if part)
    subline = esc(model or data.get("Condition", ""))
    return f'<a class="card" data-product-id="{esc(product_id)}" data-category="{esc(category)}" href="inventory/{quote(product_id)}/listing.html"><div class="visual">{badge}{media}</div><div class="details"><div>{title}<small>{subline}</small></div><span class="price">{esc(price)}</span></div></a>'


def rebuild_catalog_and_collection() -> None:
    active = [item for item in all_listings() if item.get("Active", False)]
    entries = []
    for item in active:
        product_id = str(item.get("Product ID", ""))
        if not ID_RE.fullmatch(product_id):
            continue
        entries.append({
            "Product ID": product_id,
            "Catalog URL": f"inventory/{product_id}/listing.html",
            "Title": item.get("Title", ""),
            "Category": item.get("Category", "Other"),
            "Device Series": item.get("Device Series", "other"),
            "Device Model": item.get("Device Model", ""),
            "Price (in GBP)": item.get("Price (in GBP)"),
            "Status": item.get("Status", "available"),
        })
    write_json(CATALOG, {"Listings": entries})

    source = COLLECTIONS.read_text(encoding="utf-8")
    start_marker, end_marker = "<!-- INVENTORY:START -->", "<!-- INVENTORY:END -->"
    start = source.index(start_marker) + len(start_marker)
    end = source.index(end_marker, start)
    cards = "\n" + "\n".join(collection_card(item) for item in active) + "\n" if active else "\n"
    source = source[:start] + cards + source[end:]
    atomic_text(COLLECTIONS, source)


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
        "Status": "available",
        "Active": active,
    }


def save_listing(data: dict) -> None:
    product_id = str(data["Product ID"])
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
        answer = input("Choose a number" + (" (Enter keeps current)" if current else "") + ": ").strip()
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


def ask_images(data: dict, folder: Path, editing: bool) -> None:
    current = data.get("Cover image", "")
    prompt = "Cover image file path (Enter keeps current, - clears)" if editing else "Cover image file path (optional)"
    path = input(f"{prompt}{f' [{current}]' if current else ''}: ").strip()
    if path == "-":
        data["Cover image"] = ""
    elif path:
        try:
            data["Cover image"] = copy_image(path, folder, "cover")
        except ValueError as error:
            print(error, "Keeping the existing cover image.")
    elif not editing:
        data["Cover image"] = ""

    if editing:
        current_images = data.get("Additional images", [])
        action = input("Additional image paths: Enter keeps current, - clears, or enter paths one per line and finish with a blank line: ").strip()
        if not action:
            return
        if action == "-":
            data["Additional images"] = []
            return
        paths = [action]
    else:
        current_images = []
        paths = []
        print("Additional image file paths (one per line; blank line when finished):")
    while True:
        line = input("Additional image path: ").strip()
        if not line:
            break
        paths.append(line)
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
    data["Device Series"] = choose("Device Series", SERIES, data.get("Device Series") if editing else None)
    data["Device Model"] = ask_text("Device Model", data.get("Device Model", ""), required=not editing)
    data["Description"] = ask_multiline("Description", data.get("Description", ""))
    data["Condition"] = ask_text("Condition", data.get("Condition", ""), required=not editing)
    data["Storage (optional value)"] = ask_text("Storage (optional; - clears)", str(data.get("Storage (optional value)") or "")) or None
    data["RAM (optional value)"] = ask_text("RAM (optional; - clears)", str(data.get("RAM (optional value)") or "")) or None
    if data["Storage (optional value)"] == "-":
        data["Storage (optional value)"] = None
    if data["RAM (optional value)"] == "-":
        data["RAM (optional value)"] = None
    data["Price (in GBP)"] = ask_price(data.get("Price (in GBP)"))
    data["eBay link"] = ask_text("eBay link", data.get("eBay link", ""), required=not editing)
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
        print(f"  {index}. {item.get('Product ID')} — {item.get('Title') or 'Untitled listing'} ({visibility}, {item.get('Status', 'available')})")
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
    visibility = input(f"Visible in the website catalog? [Y/n, currently {'yes' if updated.get('Active') else 'no'}]: ").strip().lower()
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
    if bool(current.get("Active")) == active:
        print(f"{current['Product ID']} is already {'active' if active else 'inactive'}.")
        return
    current["Active"] = active
    save_listing(current)
    print(f"{current['Product ID']} is now {'visible in' if active else 'removed from'} the website catalog.")


def print_menu() -> None:
    print("\nReboot Archive · Inventory Manager")
    print("1. Create a blank listing")
    print("2. Create a listing with prompts")
    print("3. Edit a listing")
    print("4. Deactivate a listing")
    print("5. Reactivate a listing")
    print("6. List inventory")
    print("7. Exit")


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
                return 0
            else:
                print("Choose a number from 1 to 7.")
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Inventory manager: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
