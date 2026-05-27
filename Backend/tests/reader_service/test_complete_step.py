import pytest
from uuid import uuid4
from Domain.Entities.User.User import User
from Domain.Entities.User.Credentials import Credentials
from Domain.Entities.RecipeBook.BookEntry import BookEntry
from Domain.Entities.RecipeBook.RecipeBook import Book


@pytest.mark.asyncio
async def test_mark_step_as_completed_success(reader_service, mock_user_repo):
    user_id, recipe_id = uuid4(), uuid4()
    book = Book(user_id=user_id, entries={recipe_id: BookEntry(recipe_id, [], [])})
    user = User(
        credentials=Credentials(id=user_id, login="test", password_hashes=["123"]),
        authored_recipes=[], recipe_book=book
    )
    await mock_user_repo.save(user)

    await reader_service.mark_step_as_completed(user_id, recipe_id, 0)
    updated_user = await mock_user_repo.get_by_id(user_id)
    assert 0 in updated_user.recipe_book.entries[recipe_id].completed_steps


@pytest.mark.asyncio
async def test_mark_step_as_completed_recipe_missing(reader_service, mock_user_repo):
    user_id, recipe_id = uuid4(), uuid4()
    user = User(
        credentials=Credentials(id=user_id, login="test", password_hashes=["123"]),
        authored_recipes=[], recipe_book=Book(user_id=user_id, entries={})
    )
    await mock_user_repo.save(user)

    with pytest.raises(ValueError, match="Recipe not found in book"):
        await reader_service.mark_step_as_completed(user_id, recipe_id, 0)
