from Application.Interfaces.IRecipeRepository import IRecipeRepository
from Application.Interfaces.IUserRepository import IUserRepository
from Application.Services.RecipeBookServices.RecipeBookService import RecipeBookService
from uuid import UUID

class ReaderService:
    def __init__(
        self,
        user_repo: IUserRepository,
        recipe_repo: IRecipeRepository,
        book_service: RecipeBookService
    ):
        self.user_repo = user_repo
        self.recipe_repo = recipe_repo
        self.book_service = book_service


    async def add_recipe_to_book(self, user_id: UUID, recipe_id: UUID):
        user = await self.user_repo.get_by_id(user_id)
        recipe = await self.recipe_repo.get_by_id(recipe_id)

        if recipe is None:
            raise ValueError("Recipe not found")

        if not await self.recipe_repo.is_published(recipe_id):
            raise ValueError("Recipe not published")

        if self.book_service.has_recipe(user.recipe_book, recipe_id):
            return

        self.book_service.add_recipe(user.recipe_book, recipe_id)
        await self.user_repo.save(user)


    async def remove_recipe_from_book(self, user_id: UUID, recipe_id: UUID):
        user = await self.user_repo.get_by_id(user_id)

        if not self.book_service.has_recipe(user.recipe_book, recipe_id):
            raise ValueError("Recipe not found in book")

        self.book_service.remove_recipe(user.recipe_book, recipe_id)
        await self.user_repo.save(user)


    async def mark_step_as_completed(self, user_id: UUID, recipe_id: UUID, step_index: int):
        user = await self.user_repo.get_by_id(user_id)

        if not self.book_service.has_recipe(user.recipe_book, recipe_id):
            raise ValueError("Recipe not found in book")

        self.book_service.mark_step_completed(user.recipe_book, recipe_id, step_index)
        await self.user_repo.save(user)


    async def mark_ingredient_as_missing(self, user_id: UUID, recipe_id: UUID, ingredient_name: str):
        user = await self.user_repo.get_by_id(user_id)

        if not self.book_service.has_recipe(user.recipe_book, recipe_id):
            raise ValueError("Recipe not found in book")
        self.book_service.mark_ingredient_missing(user.recipe_book, recipe_id, ingredient_name)
        await self.user_repo.save(user)


    async def get_missing_ingredients(self, user_id: UUID) -> list[UUID]:
        user = await self.user_repo.get_by_id(user_id)
        return self.book_service.get_all_missing_ingredients(user.recipe_book)
    

    async def unmark_step_as_completed(self, user_id: UUID, recipe_id: UUID, step_index: int):
        user = await self.user_repo.get_by_id(user_id)

        if not self.book_service.has_recipe(user.recipe_book, recipe_id):
            raise ValueError("Recipe not found in book")

        self.book_service.unmark_step_completed(user.recipe_book, recipe_id, step_index)
        await self.user_repo.save(user)


    async def unmark_ingredient_as_missing(self, user_id: UUID, recipe_id: UUID, ingredient_name: str):
        user = await self.user_repo.get_by_id(user_id)

        if not self.book_service.has_recipe(user.recipe_book, recipe_id):
            raise ValueError("Recipe not found in book")

        self.book_service.unmark_ingredient_missing(user.recipe_book, recipe_id, ingredient_name)
        await self.user_repo.save(user)


    async def get_all_book_entries(self, user_id: UUID):
        user = await self.user_repo.get_by_id(user_id)
        return self.book_service.get_all_entries(user.recipe_book)

