from abc import ABC, abstractmethod
from uuid import UUID
from Domain.Entities.Recipe.Recipe import Tag, Ingredient, Recipe
from typing import List

class IRecipeRepository(ABC):
    @abstractmethod
    async def get_by_id(self, recipe_id: UUID) -> Recipe | None: pass
    
    @abstractmethod
    async def save(self, recipe: Recipe): pass

    @abstractmethod
    async def is_published(self, recipe_id: UUID) -> bool: pass

    @abstractmethod
    async def find(
        self,
        tags: List[Tag],
        ingredients: List[Ingredient],
        query: str
    ) -> List[Recipe]:
        pass

    @abstractmethod
    async def find_by_author(self, author_id: UUID) -> List[Recipe]: pass

    @abstractmethod
    async def get_all(self) -> List[Recipe]: pass

    @abstractmethod
    async def get_all_ingredients(self) -> List[Ingredient]: pass

    @abstractmethod
    async def get_all_tags(self) -> List[Tag]: pass

    @abstractmethod
    async def get_by_ids(self, recipe_ids: List[UUID]) -> List[Recipe]: pass

    @abstractmethod
    async def delete_recipe(self, recipe_id: UUID): pass