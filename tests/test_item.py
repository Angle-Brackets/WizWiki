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


@pytest.mark.asyncio
async def test_item_malistaire_cowl_of_flux():
    # Item with many stats and special requirements
    item = await Item.get("Malistaire's Cowl of Flux")
    assert item.name == "Malistaire's Cowl of Flux"
    assert item.level_requirement == 100
    assert item.school_requirement == "Storm"

    # Check key stats
    assert item.stats.get("Max Health") == "+336"
    assert item.stats.get("Power Pip Chance") == "+10%"
    assert item.stats.get("Global Resistance") == "+10"
    assert item.stats.get("Global Armor Piercing") == "+7"
    assert item.stats.get("Shadow Pip Rating") == "+11"
    assert item.stats.get("Storm Critical Rating") == "+178"
    assert item.stats.get("Storm Damage") == "+20"
    assert item.stats.get("Shadow Damage") == "+5"
    # Critical and Damage usually have school names in them if they are icons
    # Our parser joins icons, so "Storm Critical" or similar might be the key
    assert any("Critical" in k and "Storm" in k for k in item.stats)
    assert any("Damage" in k and "Storm" in k for k in item.stats)

    # Economy
    assert item.vendor_sell_price == 2547
    assert item.is_tradeable is True
    assert item.is_auctionable is False

    # Media (should be normalized)
    assert item.image_male_url is not None
    assert "https://wiki.wizard101central.com/wiki/images" in item.image_male_url
    assert "/wiki/wiki/" not in item.image_male_url

    # Item Cards removed because the item doesn't give them.
    assert len(item.item_cards) == 0


@pytest.mark.asyncio
async def test_item_armor_of_the_cold_hearted():
    item = await Item.get("Armor of the Cold Hearted")
    print(item)
    assert item.name == "Armor of the Cold Hearted"
    assert item.level_requirement == 100
    assert item.school_requirement == "Ice"
    assert item.stats.get("Max Health") == "+975"
    assert item.stats.get("Power Pip Chance") == "+9%"
    assert "Shadow Trap" in item.item_cards


@pytest.mark.asyncio
async def test_item_ring_of_apotheosis():
    item = await Item.get("Ring of Apotheosis")
    assert item.name == "Ring of Apotheosis"
    assert item.image_url is not None
    assert item.image_male_url == item.image_url
    assert item.image_female_url == item.image_url
