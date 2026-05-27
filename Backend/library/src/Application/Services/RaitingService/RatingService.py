from Application.Interfaces.IRatingRepository import IRatingRepository
from uuid import UUID

class RatingService:
    def __init__(self, repository: IRatingRepository):
        self.repository = repository

    async def get_rating_by_id(self, user_id: UUID) -> int:
        return await self.repository.get_rating_by_id(user_id)

    async def add_rating_to_user(self, user_id: UUID, amount: int):
        await self.repository.add_rating_to_user(user_id, amount)

    async def delete_rating_from_user(self, user_id: UUID, amount: int):
        await self.repository.delete_rating_from_user(user_id, amount)
