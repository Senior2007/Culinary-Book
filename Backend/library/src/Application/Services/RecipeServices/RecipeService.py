from uuid import UUID, uuid4
from typing import List
from Domain.Entities.Recipe.Recipe import Recipe
from Domain.Entities.Recipe.RecipeContent import RecipeContent
from Domain.Entities.Recipe.Step import Step
from Domain.Entities.Recipe.Tag import Tag
from Domain.Entities.Recipe.Ingredient import Ingredient
from Application.Interfaces.IRecipeRepository import IRecipeRepository

class RecipeService:
    
    def __init__(self, recipe_repo: IRecipeRepository):
        self.recipe_repo = recipe_repo


    async def create_recipe(self, author_id: UUID, title: str) -> UUID:
        recipe = Recipe(
            id=uuid4(),
            title=title,
            author_id=author_id,
            ingredients=[],
            steps=[],
            tags=[],
            is_published=False
        )
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


    async def publish_recipe(self, recipe_id: UUID):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        recipe.is_published = True
        await self.recipe_repo.save(recipe)
    
    
    async def find_recipes(self, tags: List[Tag], ingredients: List[Ingredient], query: str) -> List[Recipe]:
        return await self.recipe_repo.find(tags, ingredients, query)
    

    async def add_image_to_step(self, recipe_id: UUID, step_index: int, image_url: str):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        if not (0 <= step_index < len(recipe.steps)):
            raise IndexError("Step index out of range")

        recipe.steps[step_index].contents.append(RecipeContent(image_url))
        await self.recipe_repo.save(recipe)

    async def remove_image_from_step(self, recipe_id: UUID, step_index: int, image_index: int):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        if not (0 <= step_index < len(recipe.steps)):
            raise IndexError("Step index out of range")

        if not (0 <= image_index < len(recipe.steps[step_index].contents)):
            raise IndexError("Image index out of range")

        recipe.steps[step_index].contents.pop(image_index)
        await self.recipe_repo.save(recipe)


    async def remove_tag(self, recipe_id: UUID, tag_name: str):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        recipe.tags = [tag for tag in recipe.tags if tag.name != tag_name]
        await self.recipe_repo.save(recipe)

    async def remove_step(self, recipe_id: UUID, step_index: int):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        if not (0 <= step_index < len(recipe.steps)):
            raise IndexError("Step index out of range")

        recipe.steps.pop(step_index)
        await self.recipe_repo.save(recipe)

    async def remove_ingredient(self, recipe_id: UUID, ingredient_name: str):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        recipe.ingredients = [ingredient for ingredient in recipe.ingredients if ingredient.name != ingredient_name]
        await self.recipe_repo.save(recipe)

    async def update_step(self, recipe_id: UUID, step_index: int, description: str):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        if not (0 <= step_index < len(recipe.steps)):
            raise IndexError("Step index out of range")

        recipe.steps[step_index].description = description
        await self.recipe_repo.save(recipe)

    async def update_step_description(self, recipe_id: UUID, step_index: int, description: str):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")

        if not (0 <= step_index < len(recipe.steps)):
            raise IndexError("Step index out of range")

        recipe.steps[step_index].description = description
        await self.recipe_repo.save(recipe)

    async def delete_recipe(self, recipe_id: UUID):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError("Recipe not found")
        await self.recipe_repo.delete_recipe(recipe_id)
