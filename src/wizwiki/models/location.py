from __future__ import annotations
from typing import List, Optional
from pydantic import Field
from .base import Resource, View


class LocationView(View):
    category: str = "Location"


class Location(Resource):
    """Represents a World, Zone, or Sublocation in Wizard101."""
    category: str = "Location"

    # Core Information
    description: Optional[str] = Field(default=None,
                                       description="A text description of the location.")
    map_url: Optional[str] = Field(default=None,
                                   description="URL pointing to the map image of the location.")

    # Relationships
    connections: List[LocationView] = Field(
        default_factory=list,
        description="Other locations that directly connect to this one.")
    sublocations: List[LocationView] = Field(
        default_factory=list,
        description="Smaller areas contained within this location.")
    parents: List[LocationView] = Field(default_factory=list,
                                        description="Larger areas that contain this location.")

    @classmethod
    async def get(cls, name: str, client: Optional['WizWikiClient'] = None) -> 'Location':
        """
        Public method to fetch a Location by name.
        """
        if client is None:
            from .. import _default_client
            client = _default_client
        return await client.get_resource(name, "Location")

    @classmethod
    def _parse(cls, html_content: str, name: str, url: str, client: 'WizWikiClient') -> Location:
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find(id="mw-content-text")

        description = None
        map_url = None
        connections = []
        sublocations = []

        if not content:
            return cls(name=name, category="Location", url=url)

        # 1. Description extraction (Robust)
        desc_target = content.find(
            lambda t: t.name in [
                "div",
                "p",
                "b",
                "td",
                "span"] and re.match(
                r"^\s*Description",
                t.get_text().strip(),
                re.I))
        if desc_target:
            full_text = desc_target.get_text(" ", strip=True)
            description = re.sub(r"^\s*Description\s*:?", "", full_text, flags=re.I).strip()

        if not description or len(description) < 20:
            for p in content.find_all(["p", "div"], recursive=False):
                p_text = p.get_text(strip=True)
                if len(p_text) > 40 and not any(x in p_text.lower()
                                                for x in ["this is a", "map", "connect", "location"]):
                    description = p_text
                    break

        # 2. Map Image extraction (Strict)
        all_imgs = content.find_all("img")

        # Priority 1: Label then search
        map_label = content.find(lambda t: re.match(r"^\s*Map", t.get_text().strip(), re.I))
        if map_label:
            img = map_label.find("img")
            if not img:
                # Search next few siblings
                curr = map_label
                for _ in range(3):
                    curr = curr.find_next(["div", "table", "p", "img"])
                    if not curr:
                        break
                    if curr.name == "img":
                        img = curr
                        break
                    img = curr.find("img")
                    if img:
                        break
            if img:
                map_url = img.get("src")

        # Skip icons if we found one mistakenly
        def is_icon(s):
            s = s.lower()
            return any(x in s for x in ["icon", "crown", "template", "category", "stub"])

        if map_url and is_icon(map_url):
            map_url = None

        # Priority 2: Explicit map filename
        if not map_url:
            for img in all_imgs:
                alt = img.get("alt", "")
                src = img.get("src", "")
                if "(Map)" in alt or "(Map)" in src:
                    map_url = src
                    break

        # Priority 3: First substantial image
        if not map_url:
            for img in all_imgs:
                src = img.get("src", "")
                if is_icon(src):
                    continue
                w = int(img.get("width", 0))
                if w > 200:
                    map_url = src
                    break

        if map_url:
            map_url = client.normalize_url(map_url)

        # 3. Connections and Sublocations
        def extract_links(header_patterns):
            links = []
            pattern = re.compile(header_patterns, re.I)
            header = content.find(
                lambda t: t.name in [
                    "h2", "h3", "b", "div", "p"] and pattern.search(
                    t.get_text().strip()))
            if header:
                # Search next siblings or inside if it's a big div
                container = header
                if len(header.find_all("a")) < 2:
                    container = header.find_next(["ul", "ol", "div", "table"])

                if container:
                    for a in container.find_all("a"):
                        link_name = a.get_text(strip=True)
                        link_href = a.get("href", "")
                        # Filter out useless links
                        if not link_name or "Edit" in link_name or ":" in link_name:
                            if ":" in link_name and "Location:" in link_name:
                                pass  # Allow Location links with namespace
                            else:
                                continue
                        if link_href:
                            full_u = client.normalize_url(link_href)
                            view = client._map_category_to_view(link_name, "Location", full_u)
                            if view not in links:
                                links.append(view)
            return links

        connections.extend(extract_links(r"^Connections$|Connect|^Locations$"))
        sublocations.extend(extract_links(r"Sublocation"))

        return cls(
            name=name,
            category="Location",
            url=url,
            description=description,
            map_url=map_url,
            connections=connections,
            sublocations=sublocations
        )
