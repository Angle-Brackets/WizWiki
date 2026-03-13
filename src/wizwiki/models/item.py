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
        import urllib.parse
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
                                    "School" in p.get_text() or "Bonus" in p.get_text() or p.get_text(strip=True) == ""):
                                school = s.capitalize()
                                break
                    if school:
                        break

            item_type = get_val_robust("Item Type") or get_val_robust("Type")
            if not item_type:
                cats = ["Hat", "Robe", "Boots", "Wand", "Athame", "Amulet", "Ring", "Deck"]
                for img in content.find_all("img"):
                    alt = img.get("alt", "")
                    m = re.match(r'\(Icon\)\s+(.*?)\.png', alt, re.I)
                    if m:
                        t = m.group(1).strip()
                        if t in cats:
                            item_type = t
                            break
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
            elif content.find(lambda t: t.name in ["b", "dd"] and "No Trade" in t.get_text()):
                tradeable = False
            elif content.find(lambda t: t.name in ["b", "dd"] and re.search(r'^Tradeable$', t.get_text().strip(), re.I)):
                tradeable = True

            auc_val = get_val_robust("Auctionable") or get_val_robust("Auction")
            if auc_val:
                auctionable = "No" not in auc_val
            elif content.find(lambda t: t.name in ["b", "dd"] and "No Auction" in t.get_text()):
                auctionable = False
            elif content.find(lambda t: t.name in ["b", "dd"] and re.search(r'^Auctionable$', t.get_text().strip(), re.I)):
                auctionable = True

            for container in content.find_all(["tr", "dd"]):
                if container.name == "tr" and container.find("dd"):
                    continue
                # Clean up the row text by removing junk icons and their alt text
                row_copy = BeautifulSoup(str(container), "html.parser")
                for img in row_copy.find_all("img"):
                    alt = img.get("alt", "").lower()
                    if any(x in alt for x in ["counter", "pip"]):
                        img.decompose()
                
                clean_text = row_copy.get_text(" ", strip=True)
                if not re.search(r'([+-]\d+?%?)', clean_text):
                    continue
                
                elements = []
                for child in container.descendants:
                    if isinstance(child, str):
                        text = child.strip()
                        parts = re.split(r'([+-]\d+%?)', text)
                        for p in parts:
                            p = p.strip()
                            if not p:
                                continue
                            if re.match(r'^[+-]\d+%?$', p):
                                elements.append(f"VAL:{p}")
                            else:
                                elements.append(f"TEXT:{p}")
                    elif child.name == 'img':
                        alt = child.get("alt", "")
                        icon_name = re.sub(
                            r'\(Icon\)|File:|\.png|\(Item\)', '', alt, flags=re.I).strip()
                        if icon_name and icon_name not in ["Gold", "Counter", "Pip"]:
                            elements.append(f"ICON:{icon_name}")
                            
                parsed_stats = []
                current_val = None
                current_keys = []
                
                for el in elements:
                    if el.startswith("VAL:"):
                        if current_val:
                            parsed_stats.append( (current_val, current_keys) )
                        current_val = el[4:]
                        current_keys = []
                    elif el.startswith("ICON:"):
                        if current_val:
                            current_keys.append(el[5:])
                    elif el.startswith("TEXT:"):
                        if current_val:
                            current_keys.append(el[5:])
                            
                if current_val:
                    parsed_stats.append( (current_val, current_keys) )
                    
                if not parsed_stats:
                    continue
                    
                if len(parsed_stats) > 1:
                    last_val, last_keys = parsed_stats[-1]
                    if last_keys:
                        shared_key = last_keys[-1]
                        for i in range(len(parsed_stats) - 1):
                            _, keys = parsed_stats[i]
                            if shared_key not in keys:
                                keys.append(shared_key)
                                
                for val, keys in parsed_stats:
                    key_str = " ".join(keys) if keys else clean_text.replace(val, "").strip()
                    stats[key_str] = val

            for img in content.find_all("img"):
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
            def extract_card_name(a_tag):
                href = a_tag.get("href", "")
                if "/Spell:" in href or "/ItemCard:" in href:
                    raw_n = a_tag.get_text(strip=True)
                    if raw_n:
                        return raw_n
                    m = re.search(r'/(?:Spell|ItemCard):([^&]+)', href)
                    if m:
                        return urllib.parse.unquote(m.group(1)).replace('_', ' ')
                return None

            item_cards_h = content.find(lambda t: t.name in ["h2", "h3"] and "Item Cards" in t.text)
            if item_cards_h:
                list_n = item_cards_h.find_next(["ul", "table", "dl"])
                if list_n:
                    for a in list_n.find_all("a"):
                        card_n = extract_card_name(a)
                        if card_n and card_n not in item_cards:
                            item_cards.append(card_n)
            elif "Item Card" in content.get_text():
                 # Fallback for infobox or other locations
                 cards_label = content.find(string=re.compile(r"Item Card", re.I))
                 if cards_label:
                     cell = cards_label.find_parent(["td", "th", "dd"])
                     if cell:
                         row = cell.find_parent(["tr", "dl"])
                         if row:
                             for a in row.find_all("a"):
                                 card_n = extract_card_name(a)
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
