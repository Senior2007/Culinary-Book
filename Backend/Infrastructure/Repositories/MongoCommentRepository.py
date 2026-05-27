from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from Application.Interfaces.ICommentRepository import ICommentRepository
from Domain.Entities.Recipe.Comment import Comment


class MongoCommentRepository(ICommentRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["comments"]

    def _to_entity(self, doc: dict) -> Comment:
        return Comment(
            id=UUID(doc["_id"]),
            recipe_id=UUID(doc["recipe_id"]),
            user_id=UUID(doc["user_id"]),
            text=doc["text"],
            image_urls=doc.get("image_urls", []),
            created_at=doc.get("created_at", ""),
        )

    async def save(self, comment: Comment) -> None:
        await self.collection.replace_one(
            {"_id": str(comment.id)},
            {
                "_id": str(comment.id),
                "recipe_id": str(comment.recipe_id),
                "user_id": str(comment.user_id),
                "text": comment.text,
                "image_urls": comment.image_urls,
                "created_at": comment.created_at,
            },
            upsert=True,
        )

    async def get_by_recipe(self, recipe_id: UUID) -> List[Comment]:
        cursor = self.collection.find({"recipe_id": str(recipe_id)}).sort(
            "created_at", 1
        )
        return [self._to_entity(doc) async for doc in cursor]

    async def get_all(self) -> List[Comment]:
        cursor = self.collection.find({}).sort("created_at", -1)
        return [self._to_entity(doc) async for doc in cursor]

    async def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        doc = await self.collection.find_one({"_id": str(comment_id)})
        return self._to_entity(doc) if doc else None

    async def delete(self, comment_id: UUID) -> None:
        await self.collection.delete_one({"_id": str(comment_id)})

    async def delete_by_recipe(self, recipe_id: UUID) -> None:
        await self.collection.delete_many({"recipe_id": str(recipe_id)})

    async def delete_by_user(self, user_id: UUID) -> None:
        await self.collection.delete_many({"user_id": str(user_id)})
