import pytest
from wizwiki import Recipe


@pytest.mark.asyncio
async def test_recipe_dragoons_cowl():
    recipe = await Recipe.get("Dragoon's Cowl")
    assert "Dragoon's Cowl" in recipe.name
    assert len(recipe.ingredients) > 0
    assert recipe.ingredients.get("Wood Button") == 2
    assert recipe.crafting_station is not None


@pytest.mark.asyncio
async def test_recipe_watchtower_hall():
    recipe = await Recipe.get("Watchtower Hall")
    assert recipe.name == "Watchtower Hall"
    assert len(recipe.ingredients) > 0
    assert recipe.crafting_station is not None


@pytest.mark.asyncio
async def test_recipe_deer_knight():
    recipe = await Recipe.get("Deer Knight")
    assert "Deer Knight" in recipe.name
    assert len(recipe.ingredients) > 0
    assert "Vendor" in str(recipe.crafting_station) or recipe.crafting_station is not None


@pytest.mark.asyncio
async def test_recipe_brimstone_revenant():
    recipe = await Recipe.get("Brimstone Revenant")
    assert "Brimstone Revenant" in recipe.name
    assert len(recipe.ingredients) > 0


@pytest.mark.asyncio
async def test_recipe_krampus():
    recipe = await Recipe.get("Krampus")
    assert "Krampus" in recipe.name
    assert recipe.category == "Recipe"


@pytest.mark.asyncio
async def test_recipe_ring_of_apotheosis():
    recipe = await Recipe.get("Ring of Apotheosis")
    assert "Ring of Apotheosis" in recipe.name
    assert recipe.cost is not None
    assert recipe.cost > 0
    assert len(recipe.vendors) > 0
