import pytest
from uuid import UUID
from Domain.Entities.Recipe.Recipe import Ingredient, Step, Tag
from Application.Services.RecipeServices.RecipeService import RecipeService


@pytest.mark.asyncio
async def test_create_recipe(recipe_service, mock_recipe_repo):
    author_id = UUID(int=0)
    recipe_id = await recipe_service.create_recipe(author_id, "Test Recipe")
    recipe = await mock_recipe_repo.get_by_id(recipe_id)
    
    assert isinstance(recipe_id, UUID)
    assert recipe.title == "Test Recipe"
    assert recipe.author_id == author_id
    assert not recipe.is_published


@pytest.mark.asyncio
async def test_add_ingredient_to_nonexistent_recipe(recipe_service):
    with pytest.raises(ValueError, match="Recipe not found"):
        await recipe_service.add_ingredient(UUID(int=999), Ingredient(name="Test"))


@pytest.mark.asyncio
async def test_add_multiple_ingredients(recipe_service, mock_recipe_repo):
    recipe_id = await recipe_service.create_recipe(UUID(int=0), "Test")
    ingredient1 = Ingredient(name="Salt")
    ingredient2 = Ingredient(name="Pepper")
    
    await recipe_service.add_ingredient(recipe_id, ingredient1)
    await recipe_service.add_ingredient(recipe_id, ingredient2)
    
    recipe = await mock_recipe_repo.get_by_id(recipe_id)
    assert len(recipe.ingredients) == 2
    assert {i.name for i in recipe.ingredients} == {"Salt", "Pepper"}


@pytest.mark.asyncio
async def test_add_step_with_contents(recipe_service, mock_recipe_repo):
    recipe_id = await recipe_service.create_recipe(UUID(int=0), "Test")
    step = Step(description="Mix ingredients", contents=[])
    
    await recipe_service.add_step(recipe_id, step)
    recipe = await mock_recipe_repo.get_by_id(recipe_id)
    
    assert len(recipe.steps) == 1
    assert recipe.steps[0].description == "Mix ingredients"


@pytest.mark.asyncio
async def test_add_image_to_step(recipe_service, mock_recipe_repo):
    # Setup recipe with steps
    recipe_id = await recipe_service.create_recipe(UUID(int=0), "Test")
    step = Step(description="Test step", contents=[])
    await recipe_service.add_step(recipe_id, step)
    
    # Add image to step
    await recipe_service.add_image_to_step(recipe_id, 0, "http://example.com/image.jpg")
    recipe = await mock_recipe_repo.get_by_id(recipe_id)
    
    assert len(recipe.steps[0].contents) == 1
    assert recipe.steps[0].contents[0].url == "http://example.com/image.jpg"


@pytest.mark.asyncio
async def test_add_image_to_invalid_step(recipe_service):
    recipe_id = await recipe_service.create_recipe(UUID(int=0), "Test")
    
    with pytest.raises(IndexError, match="Step index out of range"):
        await recipe_service.add_image_to_step(recipe_id, 999, "http://example.com/image.jpg")

@pytest.mark.asyncio
async def test_publish_recipe_flow(recipe_service, mock_recipe_repo):
    recipe_id = await recipe_service.create_recipe(UUID(int=0), "Test")
    
    # Initial state
    assert not (await mock_recipe_repo.is_published(recipe_id))
    
    # Publish
    await recipe_service.publish_recipe(recipe_id)
    
    # Verify state
    recipe = await mock_recipe_repo.get_by_id(recipe_id)
    assert recipe.is_published
    assert await mock_recipe_repo.is_published(recipe_id)
