from .client import WizWikiClient
from .models.base import View, Resource
from .models.creature import Creature
from .models.location import Location
from .models.item import Item
from .models.recipe import Recipe
from .models.spell import Spell
from .models.reagent import Reagent
from .models.jewel import Jewel
from .models.house import House
from .models.npc import NPC
from .models.quest import Quest


# Default client for convenience functions
_default_client = WizWikiClient()


async def creature(name: str) -> Creature:
    """Convenience function to fetch a Creature."""
    return await _default_client.get_creature(name)


async def item(name: str) -> Item:
    """Convenience function to fetch an Item."""
    return await _default_client.get_resource(name, "Item")


async def spell(name: str) -> Spell:
    """Convenience function to fetch a Spell."""
    return await _default_client.get_resource(name, "Spell")


async def recipe(name: str) -> Recipe:
    """Convenience function to fetch a Recipe."""
    return await _default_client.get_resource(name, "Recipe")


async def reagent(name: str) -> Reagent:
    """Convenience function to fetch a Reagent."""
    return await _default_client.get_resource(name, "Reagent")


async def jewel(name: str) -> Jewel:
    """Convenience function to fetch a Jewel."""
    return await _default_client.get_resource(name, "Jewel")


async def house(name: str) -> House:
    """Convenience function to fetch a House."""
    return await _default_client.get_house(name)


async def location(name: str) -> Location:
    """Convenience function to fetch a Location."""
    return await _default_client.get_resource(name, "Location")


async def npc(name: str) -> NPC:
    """Convenience function to fetch an NPC."""
    return await _default_client.get_npc(name)


async def quest(name: str) -> Quest:
    """Convenience function to fetch a Quest."""
    return await _default_client.get_quest(name)

__all__ = [
    "WizWikiClient",
    "Resource",
    "View",
    "Creature",
    "Item",
    "Recipe",
    "Spell",
    "Reagent",
    "Jewel",
    "Location",
    "House",
    "NPC",
    "Quest",
    "creature",
    "item",
    "recipe",
    "reagent",
    "jewel",
    "house",
    "location",
]
