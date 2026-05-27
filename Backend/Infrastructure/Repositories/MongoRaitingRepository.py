from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorDatabase
from Application.Interfaces.IRatingRepository import IRatingRepository

class MongoRaitingRepository(IRatingRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["ratings"]

    async def get_rating_by_id(self, user_id: UUID) -> int:
        rating_data = await self.collection.find_one({"_id": str(user_id)}, {"rating": 1})
        return rating_data["rating"] if rating_data else 0

    async def add_rating_to_user(self, user_id: UUID, amount: int):
        await self.collection.update_one(
            {"_id": str(user_id)},
            {"$inc": {"rating": amount}},
            upsert=True
        )

    async def delete_rating_from_user(self, user_id: UUID, amount: int):
        await self.collection.update_one(
            {"_id": str(user_id)},
            {"$inc": {"rating": -amount}},
            upsert=True
        )
    
    async def get_all_ratings(self):
        cursor = self.collection.find({}, {"_id": 1, "rating": 1})
        ratings = await cursor.to_list(length=None)
        return ratings
