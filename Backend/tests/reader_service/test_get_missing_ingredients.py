import pytest
from uuid import uuid4
from Domain.Entities.User.User import User
from Domain.Entities.User.Credentials import Credentials
from Domain.Entities.RecipeBook.BookEntry import BookEntry
from Domain.Entities.RecipeBook.RecipeBook import Book


@pytest.mark.asyncio
async def test_get_missing_ingredients(reader_service, mock_user_repo):
    user_id, recipe_id = uuid4(), uuid4()
    missing_1, missing_2 = uuid4(), uuid4()
    book = Book(user_id=user_id, entries={
        recipe_id: BookEntry(recipe_id=recipe_id, missing_ingredients=[missing_1, missing_2], completed_steps=[])
    })


    user = User(
        credentials=Credentials(id=user_id, login="test", password_hashes=["123"]),
        authored_recipes=[], recipe_book=book
    )
    await mock_user_repo.save(user)

    result = await reader_service.get_missing_ingredients(user_id)
    assert set(result) == {missing_1, missing_2}
