# Reboot Archive

Reboot Archive is a static website for discovering and buying considered vintage Apple technology. It presents restored finds, collector pieces, and familiar devices from across Apple’s design history, with the context buyers need before giving an older object a new home.

The site includes:

- A home page introducing the archive and its point of view.
- A filterable collection of currently available items, grouped by desktop, portable, music, accessories, and other categories.
- Individual product pages with photographs, specifications, condition notes, optional condition/testing/repairs reports, and a link to the corresponding eBay listing.
- A sold-items archive, so past pieces remain part of the project’s record.
- Background pages about the project, its inspection process, and ways to explore Apple hardware by era or product family, including iPhone and iPod timelines.

The website is plain HTML, CSS, and JavaScript, so it can be hosted as a static site (for example, with GitHub Pages). Product media and listing data live in the `inventory/` directory.

## Inventory manager

`inventory_manager.py` is the local publishing tool for the collection. Run it from the project root with:

```bash
python3 inventory_manager.py
```

It provides an interactive menu to:

- create blank or guided listings;
- edit a listing’s title, category, Apple series/model, description, condition, price, eBay link, images, and optional PDF report;
- show or hide listings in the current collection;
- mark a sold item as archived, including its sale date; and
- regenerate a product page from its saved JSON data.

For each item, the script assigns a sequential ID such as `RA0001`, stores the record and its media in `inventory/RA0001/`, and generates that item’s `listing.html` page. It also rebuilds `inventory/catalog.json`, updates the current listings between the inventory markers in `collections.html`, and updates the sold listings between the archive markers in `archive.html`.

On macOS, the guided workflow can open the native file picker for photographs and PDF condition reports. Elsewhere, it falls back to asking for file paths. Keep the `<!-- INVENTORY:START -->` / `<!-- INVENTORY:END -->` and `<!-- ARCHIVE:START -->` / `<!-- ARCHIVE:END -->` markers in place: the script uses them to safely update only the listing grids.

## eBay import helper

`add-ebay-listing.sh` is a separate, older helper for making a standalone listing from a public eBay item URL. It reads publicly available product metadata and eBay image URLs, asks for a display name, item type, and extra details, then creates an HTML listing and adds a card to the collection page.

Use it with:

```bash
./add-ebay-listing.sh "https://www.ebay.com/itm/..."
```

The inventory manager is the primary workflow for the current organised `inventory/` catalogue.
