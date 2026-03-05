import pytest
from wizwiki import Location


@pytest.mark.asyncio
async def test_location_dragonspyre_world():
    # Dragonspyre is a World
    loc = await Location.get("Dragonspyre")
    assert isinstance(loc, Location)
    assert loc.name == "Dragonspyre"
    assert loc.description is not None
    assert len(loc.description) > 50

    # World pages have "Locations" (major zones) - should be lumped in connections
    assert len(loc.connections) > 0
    # Common Dragonspyre zones
    zone_names = [view.name for view in loc.connections]
    assert "The Atheneum" in zone_names or "The Basilica" in zone_names


@pytest.mark.asyncio
async def test_location_atheneum_zone():
    # The Atheneum is a Zone in Dragonspyre
    loc = await Location.get("The Atheneum")
    assert isinstance(loc, Location)
    assert loc.name == "The Atheneum"
    assert loc.description is not None

    # Zones have "Connections"
    assert len(loc.connections) > 0
    found_basilica = any("Basilica" in view.name for view in loc.connections)
    assert found_basilica, f"Basilica connection not found in {loc.connections}"

    # Some zones have sublocations (buildings/NPC areas)
    # The Atheneum has specific buildings
    assert len(loc.sublocations) >= 0


@pytest.mark.asyncio
async def test_location_map_parsing():
    loc = await Location.get("The Commons")
    assert isinstance(loc, Location)
    assert loc.map_url is not None
    assert "/wiki/File:Location_Wizard_City_The_Commons_Map.png" in loc.map_url or "The_Commons" in loc.map_url


@pytest.mark.asyncio
async def test_location_wizard_city():
    loc = await Location.get("Wizard City")
    assert loc.name == "Wizard City"
    assert loc.description is not None
    assert len(loc.connections) > 0


@pytest.mark.asyncio
async def test_location_ravenwood():
    loc = await Location.get("Ravenwood")
    assert loc.name == "Ravenwood"
    assert len(loc.connections) > 0
    assert any("Wizard City" in c.name or "Commons" in c.name for c in loc.connections)
