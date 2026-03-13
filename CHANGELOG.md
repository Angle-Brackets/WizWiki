# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2026-03-12
### 🐛 Bug Fixes & Improvements
* **Robust Item Stat Parsing:**
  * Updated the crawler to iterate over `<dd>` tags in addition to `<tr>` rows. This fixes an issue where the parser would fail to extract newly formatted item stats or mash them together into an unreadable string.
  * Implemented a new DOM sequential descendant extraction strategy to accurately split strings with multiple stat pairings. For example, inline stats like `+20 [Storm] +5 [Shadow] [Damage]` are now correctly grouped and parsed as `Storm Damage: +20` and `Shadow Damage: +5` by distributing trailing shared noun icons.
* **Item Cards URL Fallback:** Fixed a bug where Item Cards (e.g., *Shadow Trap*) provided via image-only links were skipped because bounding text was empty. The parser now intelligently falls back to extracting and unquoting the card name from the link's `href` attribute (`/wiki/ItemCard:Shadow_Trap`). Scan loops were also expanded to check for cards inside `<dl>` lists.
* **School & Type Extraction:** Added resilient fallbacks allowing the parser to extract the `school` properly when spacing is stripped, and to reliably determine the `item_type` by cross-referencing infobox icon file names (`(Icon) [Type].png`). 
* **Auction & Trade Properties:** Improved boolean parsing for `tradeable` and `auctionable` flags by regex-matching specific `<b>` elements, resolving false positives caused by omitted colons in the infobox.
* **Global Image Search:** The extraction of male and female preview images was moved globally to correctly index thumbnail images placed outside of the central stat block.
* **Spell & Creature parsing improvements:** Addressed bugs with retrieval logic and media link construction for spells and creatures.

### 🧪 Testing
* Fixed assertions in the existing `test_item_malistaire_cowl_of_flux` integration test to match the new high-fidelity stat parser outputs.
* Added `test_item_armor_of_the_cold_hearted` to guarantee image-based Item Card parsing behaves as expected.
* Expanded tests across creature, item, and spell models.

## [0.1.1] - 2026-03-04
### 🚀 Features & Updates
* Initial Release.
* Added initial CI workflows and updated `pyproject.toml` configuration for package distribution.
* Updated `README.md` documentation to reflect the latest library capabilities.
