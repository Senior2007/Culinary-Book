# tests/mocks.py
import uuid
import asyncio
from typing import Dict, List, Optional
from uuid import UUID
from Domain.Entities.Recipe.Recipe import Recipe
from Domain.Entities.Recipe.Tag import Tag
from Domain.Entities.Recipe.Ingredient import Ingredient
from Domain.Entities.User.User import User
from Application.Interfaces.IRecipeRepository import IRecipeRepository
from Application.Interfaces.IUserRepository import IUserRepository


class MockRecipeRepository(IRecipeRepository):
    def __init__(self):
        self.recipes: Dict[UUID, Recipe] = {}
        self.published = set()

    async def get_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        await asyncio.sleep(0.01)
        return self.recipes.get(recipe_id)

    async def save(self, recipe: Recipe):
        await asyncio.sleep(0.01)
        self.recipes[recipe.id] = recipe
        if recipe.is_published:
            self.published.add(recipe.id)

    async def is_published(self, recipe_id: UUID) -> bool:
        await asyncio.sleep(0.01)
        return recipe_id in self.published

    async def find(
        self,
        tags: List[Tag],
        ingredients: List[Ingredient],
        query: str
    ) -> List[Recipe]:
        await asyncio.sleep(0.01)
        return [
            r for r in self.recipes.values() if 
            all(tag in r.tags for tag in tags) and
            all(ing in r.ingredients for ing in ingredients) and
            (not query or query.lower() in r.title.lower())
        ]

    async def find_by_author(self, author_id: UUID) -> List[Recipe]:
        await asyncio.sleep(0.01)
        return [r for r in self.recipes.values() if r.author_id == author_id]

    async def get_all(self) -> List[Recipe]:
        await asyncio.sleep(0.01)
        return list(self.recipes.values())

    async def get_all_ingredients(self) -> List[Ingredient]:
        await asyncio.sleep(0.01)
        ingredients = []
        seen = set()
        for recipe in self.recipes.values():
            for ingredient in recipe.ingredients:
                if ingredient.name not in seen:
                    seen.add(ingredient.name)
                    ingredients.append(ingredient)
        return ingredients

    async def get_all_tags(self) -> List[Tag]:
        await asyncio.sleep(0.01)
        tags = []
        seen = set()
        for recipe in self.recipes.values():
            if not recipe.is_published:
                continue
            for tag in recipe.tags:
                if tag.name not in seen:
                    seen.add(tag.name)
                    tags.append(tag)
        return tags

    async def get_by_ids(self, recipe_ids: List[UUID]) -> List[Recipe]:
        await asyncio.sleep(0.01)
        return [self.recipes[recipe_id] for recipe_id in recipe_ids if recipe_id in self.recipes]

    async def delete_recipe(self, recipe_id: UUID):
        await asyncio.sleep(0.01)
        if recipe_id not in self.recipes:
            raise ValueError("Recipe not found")
        del self.recipes[recipe_id]
        self.published.discard(recipe_id)


class MockUserRepository(IUserRepository):
    def __init__(self):
        self.users: Dict[UUID, User] = {}
        self.logins: Dict[str, User] = {}
        self.emails: Dict[str, User] = {}

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        await asyncio.sleep(0.01)
        return self.users.get(user_id)

    async def save(self, user: User):
        await asyncio.sleep(0.01)
        self.users[user.credentials.id] = user
        self.logins[user.credentials.login] = user
        if user.credentials.email:
            self.emails[user.credentials.email] = user

    async def get_by_login(self, login: str) -> Optional[User]:
        await asyncio.sleep(0.01)
        return self.logins.get(login)

    async def get_by_email(self, email: str) -> Optional[User]:
        await asyncio.sleep(0.01)
        return self.emails.get(email.strip().lower())

    async def get_all(self) -> List[User]:
        await asyncio.sleep(0.01)
        return list(self.users.values())
