from __future__ import annotations
from typing import Optional, Dict, List, TYPE_CHECKING
from pydantic import Field
from .base import Resource, View
from .creature import CreatureView
from .recipe import RecipeView

if TYPE_CHECKING:
    from ..client import WizWikiClient


class ItemView(View):
    category: str = "Item"


class Item(Resource):
    """Represents an equippable or usable Item in Wizard101."""
    category: str = "Item"

    # Requirements
    level_requirement: Optional[int] = Field(
        default=None, description="The minimum level required to equip or use the item.")
    school_requirement: Optional[str] = Field(
        default=None, description="The magic school required to equip or use the item.")

    # Classification and Stats
    item_type: Optional[str] = Field(default=None,
                                     description="The type of the item (e.g., Hat, Robe, Wand).")
    stats: Dict[str,
                str] = Field(default_factory=dict,
                             description="A dictionary of stat bonuses provided by the item (e.g., {'Health': '+100'}).")

    # Economy and Trading
    vendor_sell_price: Optional[int] = Field(
        default=None, description="The base gold price when selling this item to a vendor.")
    is_tradeable: bool = Field(
        default=True,
        description="Whether the item can be traded to other characters on the same account.")
    is_auctionable: bool = Field(default=True,
                                 description="Whether the item can be sold at the Bazaar.")

    # Appearance and Sources
    appearance: Optional[str] = Field(
        default=None,
        description="The visual appearance or 'Looks Like' name of the item.")
    image_male_url: Optional[str] = Field(
        default=None, description="URL to the image of the item equipped on a male character.")
    image_female_url: Optional[str] = Field(
        default=None, description="URL to the image of the item equipped on a female character.")
    dropped_by: List[CreatureView] = Field(default_factory=list,
                                           description="A list of creatures known to drop this item.")
    used_in_recipes: List[RecipeView] = Field(
        default_factory=list,
        description="A list of recipes that require this item as an ingredient.")
    item_cards: List[str] = Field(
        default_factory=list,
        description="A list of names of Item Cards provided by this item.")

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Item':
        """
        Public method to fetch an Item by name.
        """
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Item")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> Item:
        from bs4 import BeautifulSoup
        import re
        from .recipe import RecipeView

        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find(id="mw-content-text")

        level = None
        school = None
        item_type = None
        stats = {}
        price = None
        dropped_by = []
        appearance = None
        img_male = None
        img_female = None
        tradeable = True
        auctionable = True
        used_in = []
        item_cards = []

        if content:
            def get_val_robust(label_text):
                tags = content.find_all(
                    lambda t: t.name in [
                        "td", "th", "b"] and label_text in t.get_text())
                for t in tags:
                    cell = t if t.name in ["td", "th"] else t.find_parent(["td", "th"])
                    if cell:
                        l_raw = cell.get_text(strip=True)
                        l_text = l_raw.rstrip(":").strip().lower()
                        if label_text.lower() not in l_text or len(l_text) > 40:
                            continue

                        row = cell.find_parent("tr")
                        if row:
                            cells = row.find_all(["td", "th"])
                            if len(cells) >= 2:
                                val = cells[-1].get_text(strip=True)
                                if cells[-1] == cell:
                                    if ":" in l_raw:
                                        return l_raw.split(":", 1)[1].strip()
                                    return None
                                return val
                            elif len(cells) == 1:
                                if ":" in l_raw:
                                    return l_raw.split(":", 1)[1].strip()
                return None

            level_val = get_val_robust("Level Required")
            if not level_val:
                level_val = get_val_robust("Level")
            if level_val:
                m = re.search(r'(\d+)', level_val)
                if m:
                    level = int(m.group(1))

            school = get_val_robust("School")
            if not school:
                for img in content.find_all("img"):
                    alt = img.get("alt", "").lower()
                    src = img.get("src", "").lower()
                    for s in ["fire", "ice", "storm", "life", "myth", "death", "balance"]:
                        if s in alt or s in src:
                            p = img.find_parent(["td", "th"])
                            if p and (
                                    "School" in p.get_text() or "Bonus" in p.get_text() or p.get_text() == ""):
                                school = s.capitalize()
                                break
                    if school:
                        break

            item_type = get_val_robust("Item Type") or get_val_robust("Type")
            price_val = get_val_robust("Vendor Sell Price") or get_val_robust("Sell Price")
            if price_val:
                m = re.search(r'([\d,]+)', price_val)
                if m:
                    price = int(m.group(1).replace(",", ""))

            appearance = get_val_robust("Looks Like") or get_val_robust("Appearance")
            if not appearance:
                app_link = content.find("a", string=re.compile(r"Looks Like|Appearance", re.I))
                if app_link:
                    appearance = app_link.get_text(strip=True)

            trade_val = get_val_robust("Tradeable") or get_val_robust("Trade")
            if trade_val:
                tradeable = "No" not in trade_val
            auc_val = get_val_robust("Auctionable") or get_val_robust("Auction")
            if auc_val:
                auctionable = "No" not in auc_val

            for row in content.find_all("tr"):
                # Clean up the row text by removing junk icons and their alt text
                row_copy = BeautifulSoup(str(row), "html.parser")
                for img in row_copy.find_all("img"):
                    alt = img.get("alt", "").lower()
                    if any(x in alt for x in ["counter", "pip"]):
                        img.decompose()
                
                clean_text = row_copy.get_text(" ", strip=True)
                m = re.search(r'([+-]\d+%?)', clean_text)
                if not m:
                    continue
                
                val = m.group(1)
                icons = []
                for img in row.find_all("img"):
                    alt = img.get("alt", "")
                    icon_name = re.sub(
                        r'\(Icon\)|File:|\.png|\(Item\)', '', alt, flags=re.I).strip()
                    if icon_name and icon_name not in ["Gold", "Counter", "Pip", "Power Pip"]:
                        icons.append(icon_name)
                
                if icons:
                    stat_key = " ".join(icons)
                    stats[stat_key] = val
                else:
                    rest = clean_text.replace(val, "").strip()
                    if rest:
                        stats[rest] = val

                for img in row.find_all("img"):
                    alt = img.get("alt", "")
                    src = img.get("src", "")
                    if "Male" in alt:
                        img_male = client.normalize_url(src)
                    elif "Female" in alt:
                        img_female = client.normalize_url(src)

            drop_h = content.find(lambda t: t.name in ["h2", "h3", "b"] and "Dropped By" in t.text)
            if drop_h:
                list_n = drop_h.find_next(["ul", "table", "div"])
                if list_n:
                    for a in list_n.find_all("a"):
                        href = a.get("href", "")
                        if "Creature:" in href:
                            c_n = a.get_text(strip=True)
                            if not c_n:
                                continue
                            full_u = client.normalize_url(href)
                            dropped_by.append(client._map_category_to_view(c_n, "Creature", full_u))

            rec_h = content.find(lambda t: t.name in ["h2", "h3"] and "Used in Recipes" in t.text)
            if rec_h:
                list_n = rec_h.find_next(["ul", "table"])
                if list_n:
                    for a in list_n.find_all("a"):
                        href = a.get("href", "")
                        if "Recipe:" in href:
                            r_n = a.get_text(strip=True)
                            full_u = client.normalize_url(href)
                            view = RecipeView(name=r_n, category="Recipe", url=full_u)
                            view._client = client
                            used_in.append(view)

            # Item Cards extraction
            item_cards_h = content.find(lambda t: t.name in ["h2", "h3"] and "Item Cards" in t.text)
            if item_cards_h:
                list_n = item_cards_h.find_next(["ul", "table"])
                if list_n:
                    for a in list_n.find_all("a"):
                        if "/Spell:" in a.get("href", ""):
                            card_n = a.get_text(strip=True)
                            if card_n and card_n not in item_cards:
                                item_cards.append(card_n)
            elif "Item Cards" in content.get_text():
                 # Fallback for infobox or other locations
                 cards_label = content.find(string=re.compile(r"Item Cards", re.I))
                 if cards_label:
                     cell = cards_label.find_parent(["td", "th"])
                     if cell:
                         row = cell.find_parent("tr")
                         if row:
                             for a in row.find_all("a"):
                                 if "/Spell:" in a.get("href", ""):
                                     card_n = a.get_text(strip=True)
                                     if card_n and card_n not in item_cards:
                                         item_cards.append(card_n)

        return cls(
            name=name, url=url, category="Item",
            level_requirement=level, school_requirement=school, item_type=item_type,
            stats=stats, vendor_sell_price=price, dropped_by=dropped_by,
            appearance=appearance, image_male_url=img_male, image_female_url=img_female,
            is_tradeable=tradeable, is_auctionable=auctionable, used_in_recipes=used_in,
            item_cards=item_cards
        )
