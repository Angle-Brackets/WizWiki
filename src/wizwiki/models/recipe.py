from __future__ import annotations
from typing import Optional, Dict, TYPE_CHECKING
from pydantic import Field
from .base import Resource, View

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

        return cls(
            name=name,
            category="Recipe",
            url=url,
            ingredients=ingredients,
            crafting_station=crafting_station)
