from __future__ import annotations
from typing import Optional, Dict, List, TYPE_CHECKING, Union
from pydantic import BaseModel, Field
from .base import Resource, View
from .location import LocationView

if TYPE_CHECKING:
    from ..client import WizWikiClient


class CreatureView(View):
    category: str = "Creature"


class BattleStats(BaseModel):
    starting_pips: Optional[int] = None
    incoming_boost: Optional[str] = None
    incoming_resist: Optional[str] = None
    stunnable: Optional[bool] = None
    beguilable: Optional[bool] = None


class Creature(Resource):
    """Represents a Creature in Wizard101."""
    category: str = "Creature"

    # Core Entity Information
    rank: Optional[Union[str, int]] = Field(
        default=None, description="The rank or difficulty level of the creature.")
    health: Optional[int] = Field(default=None,
                                  description="The base maximum health points of the creature.")
    school: Optional[str] = Field(default=None,
                                  description="The primary magic school the creature belongs to.")
    classification: Optional[str] = Field(
        default=None, description="The creature's classification (e.g., Boss, Minion).")

    # Location and References
    location: Optional[LocationView] = Field(
        default=None, description="The primary location where this creature is found.")
    allies: List[CreatureView] = Field(
        default_factory=list,
        description="Other creatures that may fight alongside this one.")

    # Combat Statistics
    battle_stats: Optional[BattleStats] = Field(
        default=None, description="Detailed combat statistics like starting pips and resistances.")

    # Drops and Rewards
    drops: Dict[str, List[View]] = Field(
        default_factory=list, description="Categorized items that this creature may drop upon defeat.")

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Creature':
        """
        Public method to fetch a Creature by name.
        """
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Creature")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> Creature:
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(html_content, 'html.parser')

        # Initialize defaults
        rank = None
        health = None
        school = None
        classification = None
        battle_stats = BattleStats()
        location = None
        allies = []
        drops = {}

        content = soup.find(id="mw-content-text")
        if not content:
            return cls(name=name, url=url)

        # Find all tables and look for the infobox
        tables = content.find_all("table")
        infobox = None
        for t in tables:
            if "Rank" in t.get_text() and "Health" in t.get_text():
                infobox = t
                break

        if infobox:
            for row in infobox.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue

                label = cells[0].get_text(strip=True)
                value_cell = cells[-1]
                value = value_cell.get_text(strip=True)

                if "Rank" == label:
                    rank = value
                elif "Health" == label:
                    health_match = re.search(r'([\d,]+)', value)
                    if health_match:
                        health = int(health_match.group(1).replace(",", ""))
                elif "School" == label:
                    school = value
                elif "Class" == label:
                    classification = value
                elif "Starting Pips" == label:
                    pips_match = re.search(r'(\d+)', value)
                    if pips_match:
                        battle_stats.starting_pips = int(pips_match.group(1))
                elif "Incoming Boost" == label:
                    battle_stats.incoming_boost = value
                elif "Incoming Resist" == label:
                    battle_stats.incoming_resist = value
                elif "Stunable" == label:
                    battle_stats.stunnable = "Yes" in value
                elif "Beguilable" == label:
                    battle_stats.beguilable = "Yes" in value
                elif "Minions" == label:
                    for a in value_cell.find_all("a"):
                        a_name = a.get_text(strip=True)
                        if not a_name:
                            continue
                        a_href = a.get("href", "")
                        if a_href:
                            a_href = client.normalize_url(a_href)
                        allies.append(client._map_category_to_view(a_name, "Creature", a_href))
                elif "World" == label or "Location" == label:
                    if a:
                        loc_name = a.get_text(strip=True)
                        loc_href = client.normalize_url(a.get("href", ""))
                        location = client._map_category_to_view(loc_name, "Location", loc_href)

        # Categorized Drops
        # More direct approach: find labels for types and their associated lists
        categories = [
            "Hats",
            "Robes",
            "Boots",
            "Athames",
            "Amulets",
            "Rings",
            "Wands",
            "Decks",
            "Snacks",
            "Jewels",
            "Housing",
            "Reagents",
            "Treasure Cards",
            "Spellements",
            "Seeds",
            "Mounts",
            "Pets",
            "Spells"]

        # We search for any tag that has exactly the category name as text
        for cat in categories:
            # Look for headers or bold labels
            cat_tags = content.find_all(
                lambda tag: tag.name in [
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "b",
                    "div",
                    "span",
                    "td",
                    "th"] and tag.get_text(
                    strip=True) == cat)

            for cat_tag in cat_tags:
                # Find the next list (ul, table, or div with links)
                list_node = cat_tag.find_next(["ul", "table", "div"])
                if not list_node:
                    continue

                # Check if this list_node is "too far" from the header
                # If there's another header of same or higher level in between, it's not our list
                # (Simple check: is there another potential category tag in between?)

                if cat not in drops:
                    drops[cat] = []

                for a in list_node.find_all("a"):
                    d_name = a.get_text(strip=True)
                    if not d_name or d_name.startswith(
                            "File:") or "Edit" in d_name or d_name == cat:
                        continue

                    d_href = a.get("href", "")
                    if d_href:
                        d_href = client.normalize_url(d_href)

                        d_cat = "Item"
                        if "Spell:" in d_href:
                            d_cat = "Spell"
                        elif "Reagent:" in d_href:
                            d_cat = "Reagent"
                        elif "House:" in d_href:
                            d_cat = "House"

                        view = client._map_category_to_view(d_name, d_cat, d_href)
                        if view not in drops[cat]:
                            drops[cat].append(view)

                # If we found items, we can stop searching for this category tag
                if drops[cat]:
                    break

        return cls(
            name=name,
            url=url,
            rank=rank,
            health=health,
            school=school,
            classification=classification,
            location=location,
            allies=allies,
            drops=drops,
            battle_stats=battle_stats
        )
