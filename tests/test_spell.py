import pytest
from wizwiki import Spell, NPC, Quest


@pytest.mark.asyncio
async def test_spell_fire_cat():
    # Basic spell
    s = await Spell.get("Fire Cat")
    assert s.name == "Fire Cat"
    assert s.school == "Fire"
    assert s.pip_cost == "1"
    assert s.accuracy == "75%"
    assert s.description != ""
    assert "Damage" in s.type_icons
    assert s.can_be_trained is True
    assert len(s.trainers) > 0
    assert any("Falmea" in t.name for t in s.trainers)


@pytest.mark.asyncio
async def test_spell_celestial_calendar():
    # Higher level spell with quest requirement
    s = await Spell.get("Celestial Calendar")
    assert s.name == "Celestial Calendar"
    assert s.school == "Myth"
    assert s.pip_cost == "10"
    assert len(s.acquisition_sources) > 0
    assert any("Reasonings" in q.name for q in s.acquisition_sources)


@pytest.mark.asyncio
async def test_spell_drop_bear_fury():
    # Modern spell with school pips
    s = await Spell.get("Drop Bear Fury")
    assert s.name == "Drop Bear Fury"
    assert s.school == "Myth"
    assert s.pip_cost == "3"
    assert s.school_pip_cost == "1"
    # Note: Wiki currently says 'No' for PvP for this specific spell infobox
    assert s.is_pvp is False


@pytest.mark.asyncio
async def test_npc_skeleton():
    with pytest.raises(NotImplementedError, match="Parsing for NPC is not yet implemented."):
        await NPC.get("Dalia Falmea")


@pytest.mark.asyncio
async def test_quest_skeleton():
    with pytest.raises(NotImplementedError, match="Parsing for Quest is not yet implemented."):
        await Quest.get("Celestial Reasonings")


@pytest.mark.asyncio
async def test_spell_meteor_strike():
    s = await Spell.get("Meteor Strike")
    assert s.name == "Meteor Strike"
    assert s.school == "Fire"
    assert s.pip_cost == "4"
    assert "Damage" in s.type_icons


@pytest.mark.asyncio
async def test_spell_skeletal_pirate():
    s = await Spell.get("Skeletal Pirate")
    assert s.name == "Skeletal Pirate"
    assert s.school == "Death"
    assert s.pip_cost == "5"
    assert "Damage" in s.type_icons
