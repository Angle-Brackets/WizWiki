import pytest
from wizwiki import Creature


@pytest.mark.asyncio
async def test_creature_malistaire_drake():
    c = await Creature.get("Malistaire Drake")
    assert c.name == "Malistaire Drake"
    assert c.rank == "10 Boss"
    assert c.health == 8000


@pytest.mark.asyncio
async def test_creature_lost_soul():
    c = await Creature.get("Lost Soul")
    assert c.name == "Lost Soul"
    assert c.rank == "1"


@pytest.mark.asyncio
async def test_creature_kraken():
    c = await Creature.get("Kraken")
    assert c.name == "Kraken"


@pytest.mark.asyncio
async def test_creature_lady_blackhope():
    c = await Creature.get("Lady Blackhope")
    assert c.name == "Lady Blackhope"


@pytest.mark.asyncio
async def test_creature_rattlebones():
    c = await Creature.get("Rattlebones")
    assert c.name == "Rattlebones"
    assert c.battle_stats is not None


@pytest.mark.asyncio
async def test_creature_alhazred():
    c = await Creature.get("Alhazred")
    assert c.name == "Alhazred"
    assert c.classification == "Deckathalon Creature"
    assert c.school == "Balance"
    assert "Balance" in c.battle_stats.incoming_boost
    assert "Myth" in c.battle_stats.incoming_boost


@pytest.mark.asyncio
async def test_creature_malistaire_shadow():
    c = await Creature.get("Malistaire the Undying (Shadow)")
    assert c.name == "Malistaire the Undying (Shadow)"
    assert c.image_url is not None
    assert len(c.cheats) > 0
