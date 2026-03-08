import asyncio
import cloudscraper
from typing import Any, Dict
from .models.base import View, Resource
from .models.creature import Creature, CreatureView
from .models.item import Item, ItemView
from .models.recipe import Recipe, RecipeView
from .models.spell import Spell, SpellView
from .models.reagent import Reagent, ReagentView
from .models.jewel import Jewel, JewelView
from .models.house import House, HouseView
from .models.npc import NPC, NPCView
from .models.quest import Quest, QuestView
from .models.location import Location, LocationView


class WizWikiClient:
    _models: Dict[str, type[Resource]] = {
        "Creature": Creature,
        "Item": Item,
        "Recipe": Recipe,
        "Spell": Spell,
        "Reagent": Reagent,
        "Jewel": Jewel,
        "Location": Location,
        "House": House,
        "NPC": NPC,
        "Quest": Quest,
    }

    _views: Dict[str, type[View]] = {
        "Creature": CreatureView,
        "Item": ItemView,
        "Recipe": RecipeView,
        "Spell": SpellView,
        "Reagent": ReagentView,
        "Jewel": JewelView,
        "Location": LocationView,
        "House": HouseView,
        "NPC": NPCView,
        "Quest": QuestView,
    }

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://wiki.wizard101central.com/wiki/"
        self._lock = asyncio.Lock()

    async def _request(self, method: str, url: str, **kwargs) -> Any:
        async with self._lock:
            loop = asyncio.get_running_loop()
            if method.lower() == "get":
                response = await asyncio.to_thread(self.scraper.get, url, **kwargs)
            else:
                response = await asyncio.to_thread(self.scraper.request, method, url, **kwargs)

            response.raise_for_status()
            return response

    def normalize_url(self, path: str) -> str:
        """
        Normalizes a wiki path into a full URL, handling duplicate segments
        and ensuring consistency.
        """
        if not path:
            return ""
        if path.startswith("http"):
            return path

        # Remove leading wiki/ if it exists to avoid duplication with base_url
        path = path.lstrip("/")
        if path.startswith("wiki/"):
            path = path[5:]

        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _map_category_to_view(self, name: str, category: str, url: str) -> View:
        # Proper casing for Wiki categories
        if category.upper() == "NPC":
            category_key = "NPC"
        else:
            category_key = category.capitalize()

        view_cls = self._views.get(category_key, View)
        # Use original category name for the view instance
        view = view_cls(name=name, category=category_key, url=url)
        # Fix: use private attribute
        view._client = self
        return view

    async def get_creature(self, query_name: str) -> Creature:
        return await self.get_resource(query_name, "Creature")

    async def get_house(self, name: str) -> House:
        """Fetch a House by name."""
        return self.get_resource(name, "House")

    async def get_npc(self, name: str) -> NPC:
        """Fetch an NPC by name."""
        return self.get_resource(name, "NPC")

    async def get_quest(self, name: str) -> Quest:
        """Fetch a Quest by name."""
        return self.get_resource(name, "Quest")

    async def get_resource(self, query_name: str, category: str) -> Resource:
        category = category.capitalize()
        params = {
            "action": "query",
            "titles": f"{category}:{query_name}",
            "format": "json",
            "prop": "info",
            "inprop": "url",
            "redirects": 1
        }

        # Helper to resolve page info via MediaWiki API
        async def resolve_page(t):
            p = params.copy()
            p["titles"] = t
            r = await self._request("GET", f"{self.base_url}api.php", params=p)
            for page in r.json().get("query", {}).get("pages", {}).values():
                if int(page.get("pageid", -1)) > 0:
                    return page
            return None

        # 1. Primary resolution
        page_info = await resolve_page(f"{category}:{query_name}")

        # 2. Category-specific fallbacks
        if not page_info and category == "Recipe":
            # Many recipes are described on the item page itself
            page_info = await resolve_page(f"Item:{query_name}")

        if not page_info:
            raise ValueError(f"No results found for '{query_name}' in category '{category}'.")

        # 3. Fetch and parse
        full_url = page_info["fullurl"]
        best_title = page_info["title"]
        resp = await self._request("GET", full_url)

        # Resolve model class - handle cases where metadata might differ from requested category
        model_cls = self._models.get(category)
        if not model_cls:
            cat_prefix = best_title.split(":")[0] if ":" in best_title else ""
            model_cls = self._models.get(cat_prefix, Resource)

        name = best_title.split(":", 1)[1] if ":" in best_title else best_title
        name = name.replace("_", " ").strip()

        return model_cls._parse(
            html_content=resp.text,
            name=name,
            url=full_url,
            client=self
        )

    async def fetch_resource(self, view: View) -> Resource:
        return await self.get_resource(view.name, view.category)
