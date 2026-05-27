from typing import List, Optional
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase
from Domain.Entities.Recipe.Recipe import Recipe, Tag, Ingredient
from Domain.Entities.Recipe.Step import Step
from Domain.Entities.Recipe.RecipeContent import RecipeContent
from Domain.Entities.Recipe.Ingredient import Ingredient
from Application.Interfaces.IRecipeRepository import IRecipeRepository

class MongoRecipeRepository(IRecipeRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        
        self.collection = db["recipes"]

    async def get_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        recipe_data = await self.collection.find_one({"_id": str(recipe_id)})
        if recipe_data:
            return Recipe(
                id=UUID(recipe_data["_id"]),
                title=recipe_data["title"],
                author_id=UUID(recipe_data["author_id"]),
                ingredients=[
                    Ingredient(name=ingredient["name"])
                    for ingredient in recipe_data["ingredients"]
                ],
                steps=[
                    Step(
                        description=step["description"],
                        contents=[
                            RecipeContent(url=content["url"])
                            for content in step["contents"]
                        ]
                    )
                    for step in recipe_data["steps"]
                ],
                tags=[Tag(name=tag["name"]) for tag in recipe_data["tags"]],
                is_published=recipe_data["is_published"],
                cover_url=recipe_data.get("cover_url"),
            )
        return None

    async def save(self, recipe: Recipe):
        await self.collection.replace_one(
            {"_id": str(recipe.id)},
            {
                "_id": str(recipe.id),
                "title": recipe.title,
                "author_id": str(recipe.author_id),
                "ingredients": [
                    {"name": ingredient.name}
                    for ingredient in recipe.ingredients
                ],
                "steps": [
                    {
                        "description": step.description,
                        "contents": [{"url": content.url} for content in step.contents]
                    }
                    for step in recipe.steps
                ],
                "tags": [{"name": tag.name} for tag in recipe.tags],
                "is_published": recipe.is_published,
                "cover_url": recipe.cover_url,
            },
            upsert=True
        )

    async def is_published(self, recipe_id: UUID) -> bool:
        recipe_data = await self.collection.find_one({"_id": str(recipe_id)}, {"is_published": 1})
        return recipe_data and recipe_data.get("is_published", False)

    async def find(self, tags: List[Tag], ingredients: List[Ingredient], query: str) -> List[Recipe]:
        filters = {
            "is_published": True
        }

        if tags:
            filters["tags.name"] = {"$all": [tag.name for tag in tags]}

        if ingredients:
            filters["ingredients.name"] = {"$all": [ingredient.name for ingredient in ingredients]}

        if query:
            words = query.strip().split()
            filters["$and"] = [{"title": {"$regex": word, "$options": "i"}} for word in words]

        cursor = self.collection.find(filters)
        recipes = []
        async for recipe_data in cursor:
            recipes.append(Recipe(
                id=UUID(recipe_data["_id"]),
                title=recipe_data["title"],
                author_id=UUID(recipe_data["author_id"]),
                ingredients=[
                    Ingredient(name=ingredient["name"])
                    for ingredient in recipe_data["ingredients"]
                ],
                steps=[
                    Step(
                        description=step["description"],
                        contents=[
                            RecipeContent(url=content["url"])
                            for content in step["contents"]
                        ]
                    )
                    for step in recipe_data["steps"]
                ],
                tags=[Tag(name=tag["name"]) for tag in recipe_data["tags"]],
                is_published=recipe_data["is_published"],
                cover_url=recipe_data.get("cover_url"),
            ))
        return recipes

    async def find_by_author(self, author_id: UUID) -> List[Recipe]:
        cursor = self.collection.find({"author_id": str(author_id)})
        recipes = []
        async for recipe_data in cursor:
            recipes.append(await self.get_by_id(UUID(recipe_data["_id"])))
        return recipes

    async def get_all(self) -> List[Recipe]:
        cursor = self.collection.find({})
        recipes = []
        async for recipe_data in cursor:
            recipes.append(await self.get_by_id(UUID(recipe_data["_id"])))
        return recipes

    async def get_all_ingredients(self) -> List[Ingredient]:
        cursor = self.collection.aggregate([{"$unwind": "$ingredients"}, {"$group": {"_id": "$ingredients"}}])
        ingredients = []
        async for ingredient_data in cursor:
            ingredients.append(Ingredient(name=ingredient_data["_id"]["name"]))
        return ingredients

    async def get_all_tags(self) -> List[Tag]:
        cursor = self.collection.aggregate([
            {"$match": {"is_published": True}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags"}}
        ])
        tags = []
        async for tag_data in cursor:
            tags.append(Tag(name=tag_data["_id"]["name"]))
        return tags

    async def get_by_ids(self, recipe_ids: List[UUID]) -> List[Recipe]:
        cursor = self.collection.find({"_id": {"$in": [str(recipe_id) for recipe_id in recipe_ids]}})
        recipes = []
        async for recipe_data in cursor:
            recipes.append(await self.get_by_id(UUID(recipe_data["_id"])))
        return recipes

    async def delete_recipe(self, recipe_id: UUID):
        result = await self.collection.delete_one({"_id": str(recipe_id)})
        if result.deleted_count == 0:
            raise ValueError("Recipe not found")