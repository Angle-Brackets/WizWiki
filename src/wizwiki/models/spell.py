from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from pydantic import Field
from .base import Resource, View
from .npc import NPCView
from .quest import QuestView

if TYPE_CHECKING:
    from ..client import WizWikiClient


class SpellView(View):
    """View of a Spell resource."""


class Spell(Resource):
    """Represents a Spell in Wizard101."""
    category: str = "Spell"

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Spell':
        """Fetch a Spell by name."""
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Spell")

    # Basic Info
    description: Optional[str] = Field(default=None,
                                       description="The in-game description of the spell's effect.")
    school: Optional[str] = Field(default=None,
                                  description="The magic school the spell belongs to.")

    # Costs & Stats
    pip_cost: Optional[str] = Field(default=None,
                                    description="The standard pip cost to cast the spell.")
    school_pip_cost: Optional[str] = Field(
        default=None, description="The specific Archmastery school pip cost, if any.")
    accuracy: Optional[str] = Field(default=None,
                                    description="The base accuracy percentage of the spell.")
    type_icons: List[str] = Field(
        default_factory=list,
        description="List of spell type classifications (e.g., Damage, Healing, Charm).")

    # Media
    animation_gif_url: Optional[str] = Field(
        default=None, description="URL pointing to a GIF of the spell's casting animation.")
    card_image_url: Optional[str] = Field(
        default=None, description="URL to the image of the actual spell card.")

    # PvP Rules
    is_pvp: bool = Field(
        default=False,
        description="Whether the spell is allowed in Player vs Player combat.")
    pvp_requirement: Optional[str] = Field(
        default=None, description="Any specific level or rank requirements to use the spell in PvP.")

    # Acquisition and Training
    can_be_trained: bool = Field(default=False,
                                 description="Whether the spell can be trained from an NPC.")
    trainers: List[NPCView] = Field(default_factory=list,
                                    description="List of NPCs that teach this spell.")
    training_points_cost: Optional[int] = Field(
        default=None, description="The number of training points required to learn the spell.")
    training_requirements: Optional[str] = Field(
        default=None, description="Text describing prerequisites to train the spell.")
    prerequisites: List[SpellView] = Field(
        default_factory=list,
        description="Other spells that must be learned before this one.")
    acquisition_sources: List[QuestView] = Field(
        default_factory=list,
        description="Quests or other sources that reward this spell.")
    spellement_acquirable: bool = Field(
        default=False,
        description="Whether the spell can be learned via Spellement upgrading.")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> Spell:
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find(id="mw-content-text")

        if not content:
            return cls(name=name, category="Spell", url=url)

        # 1. Description extraction (Robust)
        description = ""
        desc_cell = content.find(
            lambda t: t.name in ["td", "th", "b", "div"] and "Spell Description" in t.get_text())

        if desc_cell:
            cell = desc_cell if desc_cell.name in ["td", "th"] else desc_cell.find_parent(["td", "th"])
            if cell:
                # 1a. Check next sibling (Classic Table)
                val_td = cell.find_next_sibling("td")
                if val_td:
                    description = val_td.get_text(strip=True)

                # 1b. Check if it's in the same row but not next sibling
                if not description:
                    parent_tr = cell.find_parent("tr")
                    if parent_tr:
                        tds = parent_tr.find_all("td")
                        if tds:
                            # If the label was a TH, the TD might be the value
                            description = tds[-1].get_text(strip=True)

                # 1c. Check if description is in the next row (common in some infoboxes)
                if not description or description == cell.get_text(strip=True):
                    parent_tr = cell.find_parent("tr")
                    if parent_tr:
                        next_tr = parent_tr.find_next_sibling("tr")
                        if next_tr:
                            desc_td = next_tr.find("td")
                            if desc_td:
                                description = desc_td.get_text(strip=True)

                # 1d. Fallback: same cell
                if not description or description == cell.get_text(strip=True):
                    description = cell.get_text(strip=True).replace(
                        "Spell Description", "").strip().lstrip(":").strip()

        if not description:
            # Check for generic description headers
            desc_h = content.find(
                lambda t: t.name in ["h2", "h3"] and "Description" in t.get_text())
            if desc_h:
                desc_p = desc_h.find_next("p")
                if desc_p:
                    description = desc_p.get_text(strip=True)

        # 2. Infobox Stats
        school = None
        pip_cost = None
        school_pip_cost = None
        accuracy = None
        type_icons = []
        is_pvp = False
        pvp_requirement = None
        animation_gif_url = None
        card_image_url = None

        infobox = content.find("table", class_="infobox")
        if infobox:
            for row in infobox.find_all("tr"):
                header = row.find(["th", "td"])
                if not header:
                    continue
                label = header.get_text(" ", strip=True).lower()
                value_td = row.find_all(["td", "th"])[-1]
                if not value_td:
                    continue

                # Use regex for label matching to handle spaces and variations
                if re.search(r"school\s*pip", label):
                    # Dedicated School Pip Cost row
                    text = value_td.get_text(strip=True)
                    match = re.search(r"(\d+)", text)
                    if match:
                        school_pip_cost = match.group(1)
                elif re.search(r"school", label):
                    # Primary School (skip if it looks like a pip row we already handled or if
                    # it's explicitly a pip row)
                    if "pip" in label:
                        continue
                    imgs = value_td.find_all("img")
                    for img in imgs:
                        t = img.get("title", "").replace("Icon", "").strip()
                        if t and "School Pip" not in t:
                            school = t
                            break
                    if not school:
                        school = value_td.get_text(strip=True)
                elif re.search(r"pip\s*cost", label):
                    text = value_td.get_text(strip=True)
                    match = re.search(r"(\d+)", text)
                    if match:
                        pip_cost = match.group(1)
                    # Also check for school pip info in the same row
                    sp_match = re.search(r"(\d+)\s*School Pip", text, re.I)
                    if sp_match:
                        school_pip_cost = sp_match.group(1)
                elif "accuracy" in label:
                    accuracy = value_td.get_text(strip=True)
                elif "type" in label:
                    for img in value_td.find_all("img"):
                        title = img.get("title", "")
                        if title:
                            type_icons.append(title.replace("Spell", "").strip())
                elif "pvp" in label:
                    val_text = value_td.get_text().lower()
                    is_pvp = "yes" in val_text or ("available" in val_text and "no" not in val_text)
                    if "level" in val_text:
                        pvp_requirement = value_td.get_text(strip=True)

                # Look for the card image - typically the first image in the infobox that isn't an icon
                if not card_image_url:
                    img = value_td.find("img")
                    if img and not any(x in img.get("alt", "").lower() for x in ["icon", "pip", "school"]):
                        src = img.get("src", "")
                        if src:
                            card_image_url = client.normalize_url(src)

        # 3. Animation GIF
        for img in content.find_all("img"):
            src = img.get("src", "")
            if "Spell_Animation" in src and src.endswith(".gif"):
                animation_gif_url = client.normalize_url(src)
                break

        # 4. Acquisition & Training
        # The wiki organizes acquisition info in div.column-category blocks,
        # each with a div.infobox-plain-heading label.
        can_be_trained = False
        trainers = []
        training_requirements = None
        prerequisites = []
        acquisition_sources = []
        spellement_acquirable = False
        training_points_cost = None

        for col in content.find_all("div", class_="column-category"):
            heading_el = col.find("div", class_="infobox-plain-heading")
            if not heading_el:
                continue
            heading = heading_el.get_text(" ", strip=True)
            heading_lower = heading.lower()

            if "trainer" in heading_lower:
                for a in col.find_all("a", href=re.compile(r"/NPC:")):
                    v_name = a.get_text(strip=True)
                    v_url = client.normalize_url(a["href"])
                    view = client._map_category_to_view(v_name, "NPC", v_url)
                    if view not in trainers:
                        trainers.append(view)
                if trainers:
                    can_be_trained = True

            elif "training point" in heading_lower:
                # "Training Points can purchase this Spell"
                can_be_trained = True

            elif "requirement" in heading_lower:
                # "Requirements to Train" - list of required spells
                req_texts = []
                for a in col.find_all("a", href=re.compile(r"/Spell:")):
                    s_name = a.get_text(strip=True)
                    s_url = client.normalize_url(a["href"])
                    if s_name and s_name != name:
                        p_view = client._map_category_to_view(s_name, "Spell", s_url)
                        if p_view not in prerequisites:
                            prerequisites.append(p_view)
                        req_texts.append(s_name)
                if req_texts:
                    training_requirements = ", ".join(req_texts)

            elif "prerequisite" in heading_lower:
                # "Prerequisite to Train" - spells unlocked by this spell
                # These are spells that REQUIRE this one, not prereqs of this spell
                # Some wikis also include this for reverse lookup. Skip for now.
                pass

            elif "quest" in heading_lower or "rewarded" in heading_lower or "acquisition" in heading_lower:
                for a in col.find_all("a", href=re.compile(r"/Quest:")):
                    q_name = a.get_text(strip=True)
                    q_url = client.normalize_url(a["href"])
                    view = client._map_category_to_view(q_name, "Quest", q_url)
                    if view not in acquisition_sources:
                        acquisition_sources.append(view)

            elif "spellement" in heading_lower:
                spellement_text = col.get_text(strip=True).lower()
                spellement_acquirable = "cannot" not in spellement_text

        # Fallback: look for legacy pattern with text nodes
        if not trainers and not prerequisites:
            def find_acquisition_links(pattern, namespace):
                found_items = []
                for text_node in content.find_all(string=re.compile(pattern, re.I)):
                    if text_node.parent.name in ['script', 'style']:
                        continue
                    search_areas = [
                        text_node.find_parent("table"),
                        text_node.find_parent("div"),
                        text_node.parent.find_next(["ul", "ol", "table", "div", "p"])
                    ]
                    for area in search_areas:
                        if not area:
                            continue
                        for a in area.find_all("a", href=re.compile(f"/{namespace}:")):
                            l_name = a.get_text(strip=True)
                            l_href = a.get("href")
                            if l_name and l_href:
                                l_url = client.normalize_url(l_href)
                                view = client._map_category_to_view(l_name, namespace, l_url)
                                if view not in found_items:
                                    found_items.append(view)
                return found_items

            trainers = find_acquisition_links(r"TRAINER|TRAINING SOURCE", "NPC")
            if trainers:
                can_be_trained = True
            acquisition_sources = find_acquisition_links(r"QUEST|REWARDED FROM QUEST|ACQUISITION", "Quest")

        # Spellements
        if not spellement_acquirable:
            spellement_match = content.find(string=re.compile(r"learned with Spellements", re.I))
            if spellement_match:
                spellement_acquirable = "CAN be learned" in spellement_match

        return cls(
            name=name,
            category="Spell",
            url=url,
            description=description,
            school=school,
            pip_cost=pip_cost,
            school_pip_cost=school_pip_cost,
            accuracy=accuracy,
            type_icons=type_icons,
            animation_gif_url=animation_gif_url,
            is_pvp=is_pvp,
            pvp_requirement=pvp_requirement,
            can_be_trained=can_be_trained,
            trainers=trainers,
            spellement_acquirable=spellement_acquirable,
            training_requirements=training_requirements,
            prerequisites=prerequisites,
            acquisition_sources=acquisition_sources,
            card_image_url=card_image_url
        )
