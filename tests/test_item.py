import pytest
from wizwiki import Item


@pytest.mark.asyncio
async def test_item_bonfire_headdress():
    item = await Item.get("Bonfire Headdress")
    assert item.name == "Bonfire Headdress"
    assert item.level_requirement == 45
    assert item.school_requirement == "Fire"


@pytest.mark.asyncio
async def test_item_sky_iron_hasta():
    item = await Item.get("Sky Iron Hasta")
    assert item.name == "Sky Iron Hasta"


@pytest.mark.asyncio
async def test_item_malistaire_drakes_ebon_robe():
    item = await Item.get("Malistaire Drake's Ebon Robe")
    assert item.name == "Malistaire Drake's Ebon Robe"


@pytest.mark.asyncio
async def test_item_sword_of_kings():
    item = await Item.get("Sword of Kings")
    assert item.name == "Sword of Kings"


@pytest.mark.asyncio
async def test_item_bazaar_auctionable():
    item = await Item.get("Heartsteel")
    assert item.name == "Heartsteel"
    assert item.level_requirement == 5
