import pytest
from wizwiki import WizWikiClient
from wizwiki.models.spell import Spell
from wizwiki.models.item import Item


@pytest.mark.asyncio
async def test_get_spell():
    client = WizWikiClient()
    spell = await client.get_resource("Fire Cat", "Spell")
    assert spell.name == "Fire Cat"
    assert spell.category == "Spell"
    assert isinstance(spell, Spell)


@pytest.mark.asyncio
async def test_get_item():
    client = WizWikiClient()
    item = await client.get_resource("Malistaire Drake's Ebon Robe", "Item")
    assert item.name == "Malistaire Drake's Ebon Robe"
    assert item.category == "Item"
    assert isinstance(item, Item)


@pytest.mark.asyncio
async def test_get_reagent():
    client = WizWikiClient()
    with pytest.raises(NotImplementedError, match="Parsing for Reagent is not yet implemented."):
        await client.get_resource("Black Lotus", "Reagent")


@pytest.mark.asyncio
async def test_resource_not_found():
    client = WizWikiClient()
    with pytest.raises(ValueError, match="No results found for 'NonExistentThing'"):
        await client.get_resource("NonExistentThing", "Creature")


@pytest.mark.asyncio
async def test_view_promoter_generic():
    client = WizWikiClient()
    # Create a manual view
    view = client._map_category_to_view(
        "Fire Cat", "Spell", "https://wiki.wizard101central.com/wiki/Spell:Fire_Cat")
    spell = await view.get()
    assert isinstance(spell, Spell)
    assert spell.name == "Fire Cat"
    assert spell.category == "Spell"
