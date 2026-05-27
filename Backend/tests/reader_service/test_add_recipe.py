import pytest
from uuid import UUID, uuid4
from Domain.Entities.Recipe.Recipe import Recipe
from Domain.Entities.User.User import User
from Domain.Entities.User.Credentials import Credentials
from Domain.Entities.RecipeBook.RecipeBook import Book
from Domain.Entities.RecipeBook.BookEntry import BookEntry

@pytest.mark.asyncio
async def test_add_nonexistent_recipe_to_book(reader_service, mock_user_repo):
    user_id = uuid4()
    user = User(
        credentials=Credentials(id=user_id, login="test", password_hashes=["hash123"]),
        authored_recipes=[], recipe_book=Book(user_id=user_id, entries={})
    )
    await mock_user_repo.save(user)

    with pytest.raises(ValueError, match="Recipe not found"):
        await reader_service.add_recipe_to_book(user_id, UUID(int=999))


@pytest.mark.asyncio
async def test_add_unpublished_recipe(reader_service, mock_user_repo, mock_recipe_repo):
    user_id, recipe_id = uuid4(), uuid4()
    user = User(
        credentials=Credentials(id=user_id, login="testuser", password_hashes=["hash"]),
        authored_recipes=[], recipe_book=Book(user_id=user_id, entries={})
    )
    recipe = Recipe(id=recipe_id, title="Unpublished", author_id=user_id, tags=[], ingredients=[], steps=[], is_published=False)
    await mock_user_repo.save(user)
    await mock_recipe_repo.save(recipe)

    with pytest.raises(ValueError, match="Recipe not published"):
        await reader_service.add_recipe_to_book(user_id, recipe_id)


@pytest.mark.asyncio
async def test_add_recipe_to_book_success(reader_service, mock_user_repo, mock_recipe_repo):
    user_id, recipe_id = uuid4(), uuid4()
    user = User(
        credentials=Credentials(id=user_id, login="testuser", password_hashes=["123"]),
        authored_recipes=[], recipe_book=Book(user_id=user_id, entries={})
    )
    recipe = Recipe(id=recipe_id, title="Published", author_id=uuid4(), tags=[], ingredients=[], steps=[], is_published=True)
    await mock_user_repo.save(user)
    await mock_recipe_repo.save(recipe)

    await reader_service.add_recipe_to_book(user_id, recipe_id)
    updated_user = await mock_user_repo.get_by_id(user_id)
    assert recipe_id in updated_user.recipe_book.entries


@pytest.mark.asyncio
async def test_add_recipe_to_book_duplicate(reader_service, mock_user_repo, mock_recipe_repo):
    user_id, recipe_id = uuid4(), uuid4()
    book = Book(user_id=user_id, entries={recipe_id: BookEntry(recipe_id, [], [])})
    user = User(
        credentials=Credentials(id=user_id, login="testuser", password_hashes=["123"]),
        authored_recipes=[], recipe_book=book
    )
    recipe = Recipe(id=recipe_id, title="Already Added", author_id=uuid4(), tags=[], ingredients=[], steps=[], is_published=True)
    await mock_user_repo.save(user)
    await mock_recipe_repo.save(recipe)

    await reader_service.add_recipe_to_book(user_id, recipe_id)
    updated_user = await mock_user_repo.get_by_id(user_id)
    assert len(updated_user.recipe_book.entries) == 1
