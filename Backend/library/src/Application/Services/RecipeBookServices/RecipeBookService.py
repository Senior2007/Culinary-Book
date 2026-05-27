from uuid import UUID
from Domain.Entities.RecipeBook.RecipeBook import Book
from Domain.Entities.RecipeBook.BookEntry import BookEntry


class RecipeBookService:
    def add_recipe(self, book: Book, recipe_id: UUID):
        if recipe_id not in book.entries:
            book.entries[recipe_id] = BookEntry(
                recipe_id=recipe_id,
                completed_steps=[],
                missing_ingredients=[]
            )


    def remove_recipe(self, book: Book, recipe_id: UUID):
        if recipe_id in book.entries:
            del book.entries[recipe_id]


    def has_recipe(self, book: Book, recipe_id: UUID) -> bool:
        return recipe_id in book.entries
    

    def mark_step_completed(self, book: Book, recipe_id: UUID, step_index: int):
        entry = book.entries.get(recipe_id)
        if entry is None:
            raise ValueError("Recipe not found in book")

        if step_index not in entry.completed_steps:
            entry.completed_steps.append(step_index)

    
    def mark_ingredient_missing(self, book: Book, recipe_id: UUID, ingredient_id: UUID):
        entry = book.entries.get(recipe_id)
        if entry is None:
            raise ValueError("Recipe not found in book")

        if ingredient_id not in entry.missing_ingredients:
            entry.missing_ingredients.append(ingredient_id)

    
    def get_all_missing_ingredients(self, book: Book) -> list[UUID]:
        result = []
        for entry in book.entries.values():
            result.extend(entry.missing_ingredients)
        return list(set(result))


    def unmark_step_completed(self, book: Book, recipe_id: UUID, step_index: int):
        entry = book.entries.get(recipe_id)
        if entry is None:
            raise ValueError("Recipe not found in book")

        if step_index in entry.completed_steps:
            entry.completed_steps.remove(step_index)


    def unmark_ingredient_missing(self, book: Book, recipe_id: UUID, ingredient_id: UUID):
        entry = book.entries.get(recipe_id)
        if entry is None:
            raise ValueError("Recipe not found in book")

        if ingredient_id in entry.missing_ingredients:
            entry.missing_ingredients.remove(ingredient_id)


    def get_all_entries(self, book: Book) -> list[BookEntry]:
        return list(book.entries.values())