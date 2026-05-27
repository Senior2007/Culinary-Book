import pytest
from uuid import uuid4
from Domain.Entities.User.User import User
from Domain.Entities.User.Credentials import Credentials
from Domain.Entities.RecipeBook.BookEntry import BookEntry
from Domain.Entities.RecipeBook.RecipeBook import Book


@pytest.mark.asyncio
async def test_remove_recipe_from_book_success(reader_service, mock_user_repo):
    user_id, recipe_id = uuid4(), uuid4()
    book = Book(user_id=user_id, entries={recipe_id: BookEntry(recipe_id, [], [])})
    user = User(
        credentials=Credentials(id=user_id, login="test", password_hashes=["123"]),
        authored_recipes=[], recipe_book=book
    )
    await mock_user_repo.save(user)

    await reader_service.remove_recipe_from_book(user_id, recipe_id)
    updated_user = await mock_user_repo.get_by_id(user_id)
    assert recipe_id not in updated_user.recipe_book.entries


@pytest.mark.asyncio
async def test_remove_nonexistent_recipe_from_book(reader_service, mock_user_repo):
    user_id, recipe_id = uuid4(), uuid4()
    user = User(
        credentials=Credentials(id=user_id, login="test", password_hashes=["123"]),
        authored_recipes=[], recipe_book=Book(user_id=user_id, entries={})
    )
    await mock_user_repo.save(user)

    with pytest.raises(ValueError, match="Recipe not found in book"):
        await reader_service.remove_recipe_from_book(user_id, recipe_id)
