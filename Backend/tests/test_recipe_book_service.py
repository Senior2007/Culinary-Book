import pytest
from uuid import UUID
from Domain.Entities.RecipeBook.RecipeBook import Book, BookEntry
from Application.Services.RecipeBookServices.RecipeBookService import RecipeBookService


@pytest.fixture
def empty_book():
    return Book(user_id=UUID(int=1), entries={})


@pytest.fixture
def sample_book():
    book = Book(user_id=UUID(int=1), entries={})
    recipe_id = UUID(int=100)
    book.entries[recipe_id] = BookEntry(
        recipe_id=recipe_id,
        completed_steps=[0],
        missing_ingredients=[UUID(int=200)]
    )
    return book


def test_add_and_remove_recipe(empty_book):
    service = RecipeBookService()
    recipe_id = UUID(int=100)
    
    service.add_recipe(empty_book, recipe_id)
    assert recipe_id in empty_book.entries
    assert len(empty_book.entries) == 1
    
    service.remove_recipe(empty_book, recipe_id)
    assert recipe_id not in empty_book.entries


def test_mark_step_completed(sample_book):
    service = RecipeBookService()
    recipe_id = UUID(int=100)
    
    service.mark_step_completed(sample_book, recipe_id, 1)
    entry = sample_book.entries[recipe_id]
    assert entry.completed_steps == [0, 1]


def test_mark_ingredient_missing(sample_book):
    service = RecipeBookService()
    recipe_id = UUID(int=100)
    new_ingredient_id = UUID(int=300)
    
    service.mark_ingredient_missing(sample_book, recipe_id, new_ingredient_id)
    entry = sample_book.entries[recipe_id]
    assert new_ingredient_id in entry.missing_ingredients


def test_get_all_missing_ingredients(sample_book):
    service = RecipeBookService()
    missing = service.get_all_missing_ingredients(sample_book)
    
    assert len(missing) == 1
    assert missing[0] == UUID(int=200)


def test_has_recipe_check(sample_book):
    service = RecipeBookService()
    assert service.has_recipe(sample_book, UUID(int=100)) is True
    assert service.has_recipe(sample_book, UUID(int=999)) is False