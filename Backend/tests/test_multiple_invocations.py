import pytest
from uuid import UUID
from Domain.Entities.Recipe.Recipe import Tag, Step
from Domain.Entities.User.User import User
from Domain.Entities.RecipeBook.RecipeBook import Book
from Application.Services.UserServices.ReaderService import ReaderService


@pytest.mark.asyncio
async def test_multiple_updates(recipe_service, mock_recipe_repo):
    recipe_id = await recipe_service.create_recipe(UUID(int=0), "Test")
    
    # Множественные добавления тегов
    tags = [Tag(name=f"Tag_{i}") for i in range(5)]
    for tag in tags:
        await recipe_service.add_tag(recipe_id, tag)
    
    recipe = await mock_recipe_repo.get_by_id(recipe_id)
    assert len(recipe.tags) == 5
    
    # Множественные обновления шагов
    for i in range(3):
        await recipe_service.add_step(recipe_id, Step(description=f"Step {i}", contents=[]))
    
    recipe = await mock_recipe_repo.get_by_id(recipe_id)
    assert len(recipe.steps) == 3

@pytest.mark.asyncio
async def test_multiple_publish_calls(recipe_service, mock_recipe_repo):
    recipe_id = await recipe_service.create_recipe(UUID(int=0), "Test")
    
    # Первая публикация
    await recipe_service.publish_recipe(recipe_id)
    assert await mock_recipe_repo.is_published(recipe_id)
    
    # Повторная публикация не должна вызывать ошибок
    await recipe_service.publish_recipe(recipe_id)
    assert await mock_recipe_repo.is_published(recipe_id)