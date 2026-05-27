from abc import ABC, abstractmethod
from uuid import UUID

class IRatingRepository(ABC):
    @abstractmethod
    async def get_rating_by_id(self, user_id: UUID) -> int: pass

    @abstractmethod
    async def add_rating_to_user(self, user_id: UUID, amount: int): pass

    @abstractmethod
    async def delete_rating_from_user(self, user_id: UUID, amount: int): pass