# Changelog

All notable changes to this project will be documented in this file.

## [0.1.4] - 2026-03-15
### ✨ New Fields
* **Creature — `cheats`:** A new `cheats: List[str]` field on the `Creature` model captures the full cheat text block for bosses like Malistaire.
* **Creature — `image_url`:** Creatures now expose `image_url` populated from the infobox thumbnail.
* **Spell — `trainers`, `prerequisites`, `training_requirements`, `can_be_trained`:** Spell acquisition data is now fully populated. `trainers` is a list of `NPCView` objects, `prerequisites` is a list of `SpellView` objects, and `training_requirements` is a human-readable comma-separated string of required spell names.
* **Recipe — `vendors`, `cost`:** Recipes now expose the selling `NPCView` list and the gold `cost` to purchase the recipe.

### 🐛 Bug Fixes
* **Creature Cheat Parsing:** The wiki wraps cheat content in a `div.container-green` block rather than a plain list under a heading. The parser now correctly targets those divs instead of looking for a `<b>Cheats</b>` → `<ul>` structure.
* **Spell Acquisition Parsing:** Completely rewrote trainer, prerequisite, and spellement detection to target the wiki's structured `div.column-category` layout (each labeled with `div.infobox-plain-heading`). Previously, heuristic text-node scanning missed all of these sections.
* **Recipe Cost Parsing:** Fixed `cost` always returning `None`. Recipe pages embed the gold cost as a parenthetical `(X,XXX Gold)` inside each vendor `<li>` element rather than a dedicated table cell.

### 🧪 Testing
* Added `test_creature_malistaire_shadow` asserting the `cheats` field is populated.
* Added `test_item_ring_of_apotheosis` asserting images are populated for items without gender-specific variants.
* Added `test_recipe_ring_of_apotheosis` asserting `vendors` and `cost` are correctly populated.
* Updated `test_spell_helephant` to assert `training_requirements`, `can_be_trained`, and `trainers` are all correctly populated.

## [0.1.3] - 2026-03-13
### 🐛 Bug Fixes & Improvements
* **Creature Stat Parsing:** Fixed bugs related to extracting creature properties and stats seamlessly from their table values.
  * Added logic to extract `alt` and `title` text for image elements within the value block. This correctly handles parsing properties heavily reliant on icons like `Incoming Boost` and primary `School`.
  * Relaxed the text matching expression to naturally handle variations of the creature category label (e.g., `Class` vs `Classification`).
* **Spell Description Parsing:** Addressed an issue where spell descriptions stored across separate table rows returned an empty string. The parser now intelligently traverses downwards to check the immediately following table row.

### 🧪 Testing
* Added `test_creature_alhazred` integration test to ensure robust handling of complex nested stat modifiers. 
* Upgraded assertion behavior for existing `Spell` core tests (`test_spell_fire_cat`) to assert correctly populated spell descriptions.

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
