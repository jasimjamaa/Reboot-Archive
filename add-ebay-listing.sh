#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export REBOOT_ARCHIVE_DIR="$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'This tool needs Python 3.\n' >&2
  exit 1
fi

python3 - "$@" <<'PY'
from __future__ import annotations

import html
import json
import os
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen


ROOT = Path(os.environ["REBOOT_ARCHIVE_DIR"])
COLLECTIONS = ROOT / "collections.html"


def ask(prompt: str, default: str = "") -> str:
    label = f" [{default}]" if default else ""
    answer = input(f"{prompt}{label}: ").strip()
    return answer or default


def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


class ListingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.images: list[str] = []
        self.jsonld: list[str] = []
        self._in_jsonld = False
        self._json_buffer: list[str] = []
        self._in_h1 = False
        self._h1_buffer: list[str] = []
        self.h1 = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta":
            key = (data.get("property") or data.get("name") or data.get("itemprop")).lower()
            if key and data.get("content"):
                self.meta[key] = data["content"]
                if key in {"og:image", "twitter:image", "image"}:
                    self.images.append(data["content"])
        if tag.lower() == "img":
            for key in ("data-zoom-src", "data-src", "src"):
                image = data.get(key, "")
                if image.startswith("http") and "ebayimg.com" in urlparse(image).netloc:
                    self.images.append(image)
                    break
        if tag.lower() == "script" and data.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._json_buffer = []
        if tag.lower() == "h1":
            self._in_h1 = True
            self._h1_buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._json_buffer))
            self._in_jsonld = False
        if tag.lower() == "h1" and self._in_h1:
            self.h1 = clean_text("".join(self._h1_buffer))
            self._in_h1 = False

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._json_buffer.append(data)
        if self._in_h1:
            self._h1_buffer.append(data)


def walk_products(value):
    if isinstance(value, dict):
        kind = value.get("@type", [])
        if isinstance(kind, str):
            kind = [kind]
        if any(str(item).lower() == "product" for item in kind):
            yield value
        graph = value.get("@graph")
        if graph is not None:
            yield from walk_products(graph)
        for key, child in value.items():
            if key != "@graph":
                yield from walk_products(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_products(child)


def valid_ebay_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    return host == "ebay.com" or host.endswith(".ebay.com") or bool(re.fullmatch(r"ebay\.[a-z.]+", host))


def extract(url: str):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read(15_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
    except (HTTPError, URLError, TimeoutError) as error:
        raise SystemExit(f"Could not load the eBay listing: {error}")
    source = raw.decode(charset, errors="replace")
    parser = ListingParser()
    parser.feed(source)
    products = []
    for block in parser.jsonld:
        try:
            products.extend(walk_products(json.loads(block)))
        except (json.JSONDecodeError, TypeError):
            continue
    product = products[0] if products else {}
    title = clean_text(str(product.get("name", ""))) or clean_text(parser.meta.get("og:title", "")) or parser.h1
    description = clean_text(str(product.get("description", ""))) or clean_text(parser.meta.get("og:description", "")) or clean_text(parser.meta.get("description", ""))
    images = []
    product_images = product.get("image", [])
    if isinstance(product_images, str):
        product_images = [product_images]
    if isinstance(product_images, list):
        images.extend(str(item) for item in product_images if isinstance(item, str))
    images.extend(parser.images)
    images = list(dict.fromkeys(item for item in images if item.startswith("https://") and "ebayimg.com" in urlparse(item).netloc))[:12]
    offer = product.get("offers", {})
    if isinstance(offer, list):
        offer = offer[0] if offer else {}
    price = str(offer.get("price", "")) if isinstance(offer, dict) else ""
    currency = str(offer.get("priceCurrency", "USD")) if isinstance(offer, dict) else "USD"
    item_match = re.search(r"/itm/(?:[^/?]+/)?(\d{9,15})(?:[/?]|$)", urlparse(url).path)
    item_id = item_match.group(1) if item_match else ""
    if not title:
        raise SystemExit("I couldn't find a listing title. Try a public eBay item page URL.")
    return title, description, images, price, currency, item_id


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:60].strip("-")
    return slug or "vintage-apple-item"


def picture(url: str, alt: str, class_name: str) -> str:
    return f'<img class="{class_name}" src="{html.escape(url, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="lazy">'


def build_page(title: str, original_title: str, description: str, details: list[str], images: list[str], ebay_url: str, device: str, price: str, currency: str) -> str:
    gallery = "\n".join(picture(image, title, "gallery-image") for image in images)
    if not gallery:
        gallery = '<div class="image-placeholder" role="img" aria-label="Product photo not available">Reboot Archive</div>'
    description_html = "".join(f"<p>{html.escape(part.strip())}</p>" for part in re.split(r"\n\s*\n", description) if part.strip()) or "<p>See the original eBay listing for the complete description.</p>"
    details_html = "".join(f"<li>{html.escape(item)}</li>" for item in details)
    price_html = f'<p class="price">{html.escape(price)} {html.escape(currency)}</p>' if price else ""
    canonical_title = html.escape(title)
    source_title = html.escape(original_title)
    ebay = html.escape(ebay_url, quote=True)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f5f3ee"><meta name="description" content="{html.escape(description[:250], quote=True)}"><link rel="icon" type="image/png" href="favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet"><title>{canonical_title} — Reboot Archive</title>
<style>:root{{--paper:#f5f3ee;--ink:#242622;--muted:#797a73;--line:#dcd9d1;--rust:#a45e43;--serif:'Playfair Display',Georgia,serif;--sans:'DM Sans',Arial,sans-serif}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans)}}a{{color:inherit;text-decoration:none}}.announcement{{height:34px;background:#292b26;color:#f5f3ee;display:grid;place-items:center;font-size:9px;letter-spacing:.16em;text-transform:uppercase}}.nav{{height:76px;padding:0 7.2%;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}}.brand{{display:flex;align-items:center;gap:10px}}.brand img{{width:34px;height:34px;object-fit:cover;border-radius:9px}}.brand strong{{display:block;font:600 17px var(--serif)}}.brand span span{{font:9px var(--sans);letter-spacing:.16em;text-transform:uppercase;display:block;margin-top:3px;color:var(--muted)}}.nav-links{{display:flex;gap:36px;font-size:10px;text-transform:uppercase;letter-spacing:.14em}}.nav-links a:hover{{color:var(--rust)}}main{{padding:62px 7.2% 90px}}.crumb{{font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}.layout{{display:grid;grid-template-columns:1.05fr .95fr;gap:7%;margin-top:26px;align-items:start}}.gallery{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.gallery-image{{width:100%;aspect-ratio:1/1;object-fit:contain;background:#e9e6df;padding:12px}}.gallery-image:first-child{{grid-column:1/-1;aspect-ratio:1.12/1}}.image-placeholder{{min-height:380px;grid-column:1/-1;background:#e5e4dc;display:grid;place-items:center;font:26px var(--serif);color:#858879}}.eyebrow{{font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--rust)}}h1{{font:500 clamp(36px,4vw,54px)/1.08 var(--serif);letter-spacing:-.04em;margin:14px 0}}.device{{font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}.price{{font:500 20px var(--serif);margin:20px 0}}.description{{font-size:12px;line-height:1.9;color:#62645e;border-top:1px solid var(--line);padding-top:17px;margin-top:22px}}.description p{{margin:0 0 12px}}.details{{font-size:11px;line-height:1.8;color:#62645e;padding-left:18px}}.source-title{{font-size:10px;color:var(--muted);line-height:1.7}}.ebay-button{{display:flex;justify-content:space-between;align-items:center;margin-top:27px;padding:17px 20px;background:var(--ink);color:white;text-transform:uppercase;letter-spacing:.13em;font-size:9px;transition:.2s}}.ebay-button:hover{{background:var(--rust)}}.footnote{{font-size:9px;color:var(--muted);margin-top:12px}}footer{{border-top:1px solid var(--line);padding:25px 7.2%;font-size:9px;color:var(--muted)}}@media(max-width:760px){{.nav{{padding:0 5%;height:68px}}.nav-links{{gap:14px;font-size:8px}}.nav-links a:nth-child(2){{display:none}}main{{padding:38px 6% 65px}}.layout{{grid-template-columns:1fr;gap:34px}}.gallery-image:first-child{{aspect-ratio:1.1/1}}.image-placeholder{{min-height:280px}}}}@media(max-width:430px){{.nav-links a:nth-child(3){{display:none}}}}</style></head>
<body><div class="announcement">A second life for the objects that changed everything</div><header class="nav"><a class="brand" href="index.html"><img src="favicon.png" alt=""><span><strong>Reboot Archive</strong><span>Vintage Apple, reimagined</span></span></a><nav class="nav-links" aria-label="Main navigation"><a href="collections.html">The collection</a><a href="story.html">Our story</a><a href="explore.html">Explore</a></nav></header>
<main><a class="crumb" href="collections.html">← Back to the collection</a><div class="layout"><div class="gallery">{gallery}</div><section><div class="eyebrow">Curated vintage · {html.escape(device)}</div><h1>{canonical_title}</h1><div class="source-title">Original eBay title: {source_title}</div>{price_html}<div class="description">{description_html}</div>{f'<ul class="details">{details_html}</ul>' if details else ''}<a class="ebay-button" href="{ebay}" target="_blank" rel="noopener noreferrer"><span>View on eBay</span><span aria-hidden="true">↗</span></a><p class="footnote">Availability, condition, and purchase details are shown on eBay.</p></section></div></main><footer>Reboot Archive · Objects with a past, ready for what’s next.</footer></body></html>'''


def main() -> None:
    ebay_url = sys.argv[1].strip() if len(sys.argv) > 1 else input("eBay listing URL: ").strip()
    if not ebay_url.startswith(("https://", "http://")) or not valid_ebay_url(ebay_url):
        raise SystemExit("Enter a full eBay listing URL (for example, https://www.ebay.com/itm/...).")
    print("Reading listing details and photos from eBay...")
    original_title, description, images, price, currency, item_id = extract(ebay_url)
    print(f"Found: {original_title}")
    custom_title = ask("Custom name", original_title)
    device_options = [("1", "Desktop"), ("2", "Portable"), ("3", "Music"), ("4", "Accessories")]
    print("Device type: " + "  ".join(f"{number}) {label}" for number, label in device_options))
    selection = ask("Choose a type", "1")
    device = next((label for number, label in device_options if selection == number), None)
    if device is None:
        raise SystemExit("Choose 1, 2, 3, or 4 for the device type.")
    print("Additional details (one per line; press Enter on a blank line when finished):")
    details = []
    while True:
        line = input().strip()
        if not line:
            break
        details.append(line)

    custom_title = custom_title.strip()
    listing_key = item_id or slugify(original_title)
    filename = f"listing-{listing_key}.html"
    page_path = ROOT / filename
    if not COLLECTIONS.is_file():
        raise SystemExit(f"Collections page not found: {COLLECTIONS}")
    page_html = build_page(custom_title, original_title, description, details, images, ebay_url, device, price, currency)
    safe_title = html.escape(custom_title)
    if images:
        card_media = picture(images[0], custom_title, "listing-photo")
    else:
        card_media = '<span class="listing-placeholder">Reboot<br>Archive</span>'
    card = f'<a class="card generated-listing" data-listing-id="{html.escape(listing_key, quote=True)}" data-category="{device.lower()}" href="{quote(filename)}"><div class="visual"><span class="tag">From eBay</span>{card_media}</div><div class="details"><div>{safe_title}<small>{html.escape(device)} · View on eBay</small></div><span class="price">↗</span></div></a>'
    collection_html = COLLECTIONS.read_text(encoding="utf-8")
    marker = '<section class="grid" aria-label="Products">'
    if marker not in collection_html:
        raise SystemExit("Could not find the product grid in collections.html; no changes were made.")
    identity = f'data-listing-id="{html.escape(listing_key, quote=True)}"'
    existing = re.search(r'<a\b(?=[^>]*class="[^"]*generated-listing[^"]*")(?=[^>]*' + re.escape(identity) + r')[^>]*>.*?</a>', collection_html, re.S)
    if existing:
        collection_html = collection_html[:existing.start()] + card + collection_html[existing.end():]
    else:
        collection_html = collection_html.replace(marker, marker + "\n" + card, 1)
    image_css = '.listing-photo{width:72%;height:78%;object-fit:contain;filter:drop-shadow(0 12px 10px #35352b20)}.listing-placeholder{font:500 22px/1.3 var(--serif);text-align:center;color:#828579}'
    if ".listing-photo{" not in collection_html:
        collection_html = collection_html.replace(".visual svg{", image_css + ".visual svg{", 1)
    if 'data-filter="accessories"' not in collection_html:
        collection_html = collection_html.replace('</div><span class="count"', '<button class="filter" aria-pressed="false" data-filter="accessories">Accessories</button></div><span class="count"', 1)
    if "count.textContent=`${cards.length} objects`" not in collection_html:
        collection_html = collection_html.replace("const filters=[...document.querySelectorAll('.filter')],cards=[...document.querySelectorAll('.card')],count=document.querySelector('.count');", "const filters=[...document.querySelectorAll('.filter')],cards=[...document.querySelectorAll('.card')],count=document.querySelector('.count');count.textContent=`${cards.length} objects`;", 1)
    if 'const initialCategory=' not in collection_html and 'filters.forEach(button=>button.addEventListener' in collection_html:
        event_line = re.search(r"filters\.forEach\(button=>button\.addEventListener\('click'.*?\n", collection_html)
        if event_line:
            collection_html = collection_html[:event_line.end()] + "const initialCategory=new URLSearchParams(location.search).get('category');if(initialCategory){const initialFilter=filters.find(button=>button.dataset.filter===initialCategory);if(initialFilter)initialFilter.click()}\n" + collection_html[event_line.end():]

    def atomic_write(path: Path, content: str) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as output:
            output.write(content)
            temp_path = Path(output.name)
        temp_path.replace(path)

    atomic_write(page_path, page_html)
    atomic_write(COLLECTIONS, collection_html)
    print(f"Created product page: {page_path}")
    print(f"Added {custom_title} to: {COLLECTIONS}")
    print(f"Photos found: {len(images)}")


if __name__ == "__main__":
    main()
PY
