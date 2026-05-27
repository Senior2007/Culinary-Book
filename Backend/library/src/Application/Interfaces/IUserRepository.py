from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from Domain.Entities.User.User import User

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User: pass

    @abstractmethod
    async def save(self, user: User): pass

    @abstractmethod
    async def get_by_login(self, login: str): pass

    @abstractmethod
    async def get_by_email(self, email: str): pass

    @abstractmethod
    async def get_all(self) -> List[User]: pass
