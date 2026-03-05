import pytest
import wizwiki
from wizwiki import Creature, Item, Spell, Recipe


@pytest.mark.asyncio
async def test_top_level_convenience_functions():
    # Test wizwiki.creature
    c = await wizwiki.creature("Lost Soul")
    assert isinstance(c, Creature)
    assert c.name == "Lost Soul"

    # Test wizwiki.item
    i = await wizwiki.item("Bonfire Headdress")
    assert isinstance(i, Item)
    assert i.name == "Bonfire Headdress"

    # Test wizwiki.spell
    s = await wizwiki.spell("Fire Cat")
    assert isinstance(s, Spell)
    assert s.name == "Fire Cat"

    # Test wizwiki.recipe
    r = await wizwiki.recipe("Dragoon's Cowl")
    assert isinstance(r, Recipe)
    assert "Dragoon's Cowl" in r.name


@pytest.mark.asyncio
async def test_model_get_methods():
    # Test Creature.get
    c = await Creature.get("Lost Soul")
    assert isinstance(c, Creature)
    assert c.name == "Lost Soul"

    # Test Item.get
    i = await Item.get("Bonfire Headdress")
    assert isinstance(i, Item)
    assert i.name == "Bonfire Headdress"

    # Test Spell.get
    s = await Spell.get("Fire Cat")
    assert isinstance(s, Spell)
    assert s.name == "Fire Cat"
