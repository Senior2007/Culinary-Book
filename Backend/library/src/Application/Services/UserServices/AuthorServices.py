from uuid import UUID, uuid4
from Domain.Entities.Recipe.Recipe import Recipe
from Domain.Entities.Recipe.Step import Step
from Domain.Entities.Recipe.Tag import Tag
from Domain.Entities.Recipe.Ingredient import Ingredient
from Domain.Entities.Recipe.RecipeContent import RecipeContent
from Application.Interfaces.IRecipeRepository import IRecipeRepository


class AuthorServices:

    def __init__(self, recipe_repo: IRecipeRepository):
        self.recipe_repo = recipe_repo


    async def create_recipe(self, author_id: UUID, title: str, cover_url: str | None = None) -> UUID:
        recipe = Recipe(
            id=uuid4(),
            title=title,
            author_id=author_id,
            ingredients=[],
            steps=[],
            tags=[],
            is_published=False,
            cover_url=cover_url,
        )
        await self.recipe_repo.save(recipe)
        return recipe.id

    async def save_recipe(self, title: str, recipe_id: UUID, cover_url: str | None = None) -> UUID:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        recipe.title = title
        if cover_url is not None:
            recipe.cover_url = cover_url or None
        await self.recipe_repo.save(recipe)
        return recipe.id


    async def add_ingredient(self, recipe_id: UUID, ingredient: Ingredient):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        recipe.ingredients.append(ingredient)
        await self.recipe_repo.save(recipe)


    async def add_step(self, recipe_id: UUID, step: Step):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        recipe.steps.append(step)
        await self.recipe_repo.save(recipe)


    async def add_tag(self, recipe_id: UUID, tag: Tag):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        recipe.tags.append(tag)
        await self.recipe_repo.save(recipe)


    async def add_image_to_step(self, recipe_id: UUID, step_index: int, image_url: str):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        if step_index >= len(recipe.steps):
            raise ValueError("Step index out of bounds")

        step = recipe.steps[step_index]
        recipe_content = RecipeContent(url=image_url)
        step.contents.append(recipe_content)
        await self.recipe_repo.save(recipe)


    async def publish_recipe(self, recipe_id: UUID):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        recipe.is_published = True
        await self.recipe_repo.save(recipe)


    async def get_recipe_by_id(self, recipe_id: UUID):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        return recipe


    async def get_user_recipes(self, author_id: UUID):
        return await self.recipe_repo.find_by_author(author_id)

    async def get_all_recipes(self):
        return await self.recipe_repo.get_all()

    async def get_all_ingredients(self):
        return await self.recipe_repo.get_all_ingredients()

    async def get_all_tags(self):
        return await self.recipe_repo.get_all_tags()
    
    async def is_author(self, recipe_id: UUID, author_id: UUID) -> bool:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            return False
        return recipe.author_id == author_id
