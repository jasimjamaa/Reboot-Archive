# Reboot Archive

Reboot Archive is a curated online archive for vintage Apple technology. It gives restored, collectible, and well-kept Apple devices a considered second chapter, pairing each object with clear photography, practical condition information, and its place in Apple’s design history.

The project is a static website: it is built with HTML, CSS, and JavaScript and can be hosted on any static hosting provider, including GitHub Pages.

## What the website provides

The website includes:

- A home page introducing the archive and its point of view.
- A filterable collection of currently available devices, grouped into desktop, portable, music, accessories, and other categories.
- Dedicated listing pages with product photography, specifications, condition notes, optional testing and repairs reports, pricing, and eBay links.
- A sold-items archive that keeps past listings available as part of the record.
- Background pages covering the archive's story, inspection approach, and Apple product history, including interactive iPhone and iPod timelines.

Each page uses shared navigation and external page-specific assets. Stylesheets are in `assets/css/`, interactive page scripts are in `assets/js/`, and shared navigation and listing-search assets remain at the project root.

## Project structure

```text
.
├── assets/
│   ├── css/                 # Page and listing stylesheets
│   └── js/                  # Page-specific interactive scripts
├── inventory/
│   ├── catalog.json         # Generated catalogue summary
│   ├── sequence.json        # Next Reboot Archive product number
│   └── RA0001/              # One listing's data, media, and generated page
├── inventory_manager.py     # Interactive listing publisher
├── collections.html         # Current collection page
├── archive.html             # Sold-items archive page
└── *.html                   # Remaining site pages
```

## Inventory Manager

`inventory_manager.py` is the local publishing tool for product listings. It manages listing data and media, builds accessible HTML product pages, and keeps the collection and archive pages in sync.

Run it from the project root:

```bash
python3 inventory_manager.py
```

The manager presents an interactive menu with these options:

1. Create a blank listing.
2. Create a listing with guided prompts.
3. Edit an existing listing.
4. Hide a listing from the current collection.
5. Show an eligible listing in the current collection.
6. View the current inventory.
7. Archive a sold listing and record its sale date.
8. Regenerate a listing page from its saved data.
9. Exit.

### Creating and editing listings

The guided workflow asks for the listing title, category, device family and model, description, condition, optional storage and memory details, price, eBay URL, photographs, and an optional PDF condition report. On macOS, it opens the system file picker for images and PDFs; on other systems, enter file paths when prompted.

Each listing receives the next sequential ID, such as `RA0001`, and is stored in `inventory/<product-id>/`. A listing folder contains:

- `listing.json` — the source record for the item.
- `description.txt` — a plain-text copy of the description.
- `listing.html` — the generated product page.
- `cover.*` and `image-*.*` — copied product photography.
- `condition-report.pdf` — the optional report, when supplied.

The manager uses the data in `listing.json` as the source of truth. If a page is changed manually, use **Regenerate a listing from JSON** to restore a page from its saved listing data.

### Publishing behaviour

Whenever a listing is created, edited, shown, hidden, archived, or regenerated, the manager:

- Generates formatted HTML that links to the shared `assets/css/listing.css` stylesheet and `navigation.js` script.
- Rebuilds `inventory/catalog.json`.
- Updates the current listing cards between `<!-- INVENTORY:START -->` and `<!-- INVENTORY:END -->` in `collections.html`.
- Updates sold listing cards between `<!-- ARCHIVE:START -->` and `<!-- ARCHIVE:END -->` in `archive.html`.

Do not remove those marker comments. They allow the manager to replace only the listing grids while preserving the rest of each page.

Archiving a listing marks it as sold, removes it from the active collection, records its sale date, and adds it to the archive. Archived listings cannot be reactivated in the current collection.

## Formatting and checks

The repository uses Prettier for HTML, CSS, JavaScript, JSON, and Markdown, plus Black and Ruff for Python. Configuration lives in `.prettierrc.json` and `pyproject.toml`.

After installing the development tools, the common commands are:

```bash
npm install
npm run format:check
npm run format
npm run lint:python
npm run format:python
```

The Inventory Manager emits formatted listing HTML directly, so generated listing pages do not depend on a separate formatting step.
