import pytest
from wizwiki.client import WizWikiClient
from wizwiki.models.base import View


@pytest.mark.asyncio
async def test_creature_fetch():
    client = WizWikiClient()
    creature = await client.get_creature("Lost Soul")
    assert creature.name == "Lost Soul"
    assert creature.category == "Creature"

    # Test Battle Stats
    if creature.battle_stats:
        from wizwiki.models.creature import BattleStats
        assert isinstance(creature.battle_stats, BattleStats)

    # Test Categorized Drops
    assert isinstance(creature.drops, dict)
    # Check for some common categories
    assert any(cat in creature.drops for cat in ["Hats", "Robes", "Athames", "Snacks", "Reagents"])

    # Test Allies
    # Lost Soul might not have allies, but it has drops
    assert isinstance(creature.drops, dict)

    # Test View conversion
    if "Hats" in creature.drops:
        drop_view = creature.drops["Hats"][0]
        assert isinstance(drop_view, View)
        assert drop_view._client is not None

        # Test get()
        item = await drop_view.get()
        assert item.name == drop_view.name
