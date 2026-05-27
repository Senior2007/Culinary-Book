from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from Domain.Entities.Recipe.Comment import Comment


class ICommentRepository(ABC):
    @abstractmethod
    async def save(self, comment: Comment) -> None:
        pass

    @abstractmethod
    async def get_by_recipe(self, recipe_id: UUID) -> List[Comment]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Comment]:
        pass

    @abstractmethod
    async def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        pass

    @abstractmethod
    async def delete(self, comment_id: UUID) -> None:
        pass

    @abstractmethod
    async def delete_by_recipe(self, recipe_id: UUID) -> None:
        pass
