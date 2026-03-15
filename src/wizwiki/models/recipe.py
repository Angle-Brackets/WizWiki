from __future__ import annotations
from typing import Optional, Dict, List, TYPE_CHECKING
from pydantic import Field
from .base import Resource, View
from .npc import NPCView

if TYPE_CHECKING:
    from ..client import WizWikiClient


class RecipeView(View):
    category: str = "Recipe"


class Recipe(Resource):
    """Represents a Crafting Recipe in Wizard101."""
    category: str = "Recipe"

    # Crafting Requirements
    ingredients: Dict[str, int] = Field(
        default_factory=dict, description="A dictionary mapping required ingredient names to their quantities.")
    crafting_station: Optional[str] = Field(
        default=None, description="The specific crafting station needed to create this recipe.")
    vendors: List[NPCView] = Field(
        default_factory=list, description="NPCs that sell this recipe.")
    cost: Optional[int] = Field(
        default=None, description="The gold cost to purchase the recipe.")

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Recipe':
        """
        Public method to fetch a Recipe by name.
        """
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Recipe")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> Recipe:
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(html_content, 'html.parser')
        ingredients = {}
        crafting_station = None
        vendors = []
        cost = None

        content = soup.find(id="mw-content-text")
        if content:
            # Find Ingredients section
            ing_header = content.find(
                lambda tag: tag.name in [
                    "h2", "h3", "h4", "b"] and "Ingredients" in tag.text)
            if ing_header:
                container = ing_header.find_next(["div", "ul", "table", "p"])
                if container:
                    text = container.get_text(" ", strip=True)
                    text = re.sub(r'\s+', ' ', text)
                    matches = re.finditer(r'(\d+)\s*(?:x\s*)?([^0-9\n,;.]+)', text)
                    for m in matches:
                        qty = int(m.group(1))
                        ing_name = m.group(2).strip()
                        ing_name = re.split(r'\s{2,}', ing_name)[0]
                        if ing_name:
                            ingredients[ing_name] = qty

            # Find Crafting Station in infobox
            station_label = content.find(string=re.compile(r"Station", re.I))
            if station_label:
                cell = station_label.find_parent(["td", "th"])
                if cell:
                    row = cell.find_parent("tr")
                    if row:
                        text = row.get_text(" ", strip=True)
                        m = re.search(
                            r'Station\s*:\s*(.+?)(?=\s*(?:Cooldown\s*Time|Rank|Vendor\(s\)|Crafting|$))', text, re.I)
                        if m:
                            crafting_station = m.group(1).strip().lstrip(":").strip()
                        else:
                            val = text.split("Station",
                                             1)[-1].split("Cooldown",
                                                          1)[0].split("Rank",
                                                                      1)[0].lstrip(":").strip()
                            if val:
                                crafting_station = val

            if not crafting_station and "Crafted at Vendor" in content.get_text():
                crafting_station = "Crafted at Vendor"

            # Vendors and Cost
            # The wiki stores vendor info in a <b>Vendor(s):</b> tag followed by a <ul>.
            # Cost is embedded in the <li> text as "(X Gold)".
            vendor_b = content.find(
                lambda t: t.name == "b" and re.search(r"Vendor\(s\)\s*:?", t.get_text(), re.I)
            )
            if vendor_b:
                # Vendor list is the next <ul> after the <b> tag
                vendor_ul = vendor_b.find_next("ul")
                if vendor_ul:
                    for li in vendor_ul.find_all("li"):
                        # Extract NPC link
                        a = li.find("a", href=re.compile(r"/NPC:"))
                        if a:
                            v_name = a.get_text(strip=True)
                            v_url = client.normalize_url(a["href"])
                            vendors.append(client._map_category_to_view(v_name, "NPC", v_url))
                        # Extract cost from parenthetical text in the li
                        if cost is None:
                            li_text = li.get_text(" ", strip=True)
                            m = re.search(r"\(([\d,]+)\s*Gold\)", li_text, re.I)
                            if m:
                                cost = int(m.group(1).replace(",", ""))

            # Fallback: try old-style infobox row for Vendor(s)
            if not vendors:
                vendor_label = content.find(string=re.compile(r"Vendor\(s\)", re.I))
                if vendor_label:
                    cell = vendor_label.find_parent(["td", "th"])
                    if cell:
                        parent_tr = cell.find_parent("tr")
                        target_cell = cell.find_next_sibling("td") or (
                            parent_tr.find_all(["td", "th"])[-1] if parent_tr else None
                        )
                        if target_cell:
                            for a in target_cell.find_all("a", href=re.compile(r"/NPC:")):
                                v_name = a.get_text(strip=True)
                                v_url = client.normalize_url(a.get("href"))
                                vendors.append(client._map_category_to_view(v_name, "NPC", v_url))

            # Fallback: try old-style "Cost" row
            if cost is None:
                cost_label = content.find(string=re.compile(r"^Cost$", re.I))
                if cost_label:
                    cell = cost_label.find_parent(["td", "th"])
                    if cell:
                        val_text = ""
                        next_td = cell.find_next_sibling("td")
                        if next_td:
                            val_text = next_td.get_text(strip=True)
                        else:
                            parent_tr = cell.find_parent("tr")
                            if parent_tr:
                                val_text = parent_tr.find_all(["td", "th"])[-1].get_text(strip=True)
                        if val_text:
                            m = re.search(r"([\d,]+)", val_text)
                            if m:
                                cost = int(m.group(1).replace(",", ""))

        return cls(
            name=name,
            category="Recipe",
            url=url,
            ingredients=ingredients,
            crafting_station=crafting_station,
            vendors=vendors,
            cost=cost)
