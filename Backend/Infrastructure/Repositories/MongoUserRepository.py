from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from Domain.Entities.User.User import User
from Application.Interfaces.IUserRepository import IUserRepository
from Domain.Entities.User.Credentials import Credentials
from Domain.Entities.RecipeBook.RecipeBook import Book
from Domain.Entities.RecipeBook.BookEntry import BookEntry


class MongoUserRepository(IUserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    def _build_user(self, user_data: dict) -> User:
        creds = user_data["credentials"]
        return User(
            credentials=Credentials(
                id=UUID(creds["id"]),
                login=creds["login"],
                password_hashes=creds["password_hashes"],
                email=creds.get("email", ""),
                is_admin=creds.get("is_admin", False),
                is_banned=creds.get("is_banned", False),
            ),
            authored_recipes=[UUID(recipe_id) for recipe_id in user_data["authored_recipes"]],
            recipe_book=Book(
                user_id=UUID(user_data["recipe_book"]["user_id"]),
                entries={
                    UUID(entry_id): BookEntry(
                        recipe_id=UUID(entry["recipe_id"]),
                        completed_steps=entry["completed_steps"],
                        missing_ingredients=[
                            ingredient for ingredient in entry["missing_ingredients"]
                        ],
                    )
                    for entry_id, entry in user_data["recipe_book"]["entries"].items()
                },
            ),
        )

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        user_data = await self.collection.find_one({"_id": str(user_id)})
        if user_data:
            return self._build_user(user_data)
        return None

    async def save(self, user: User):
        await self.collection.replace_one(
            {"_id": str(user.credentials.id)},
            {
                "_id": str(user.credentials.id),
                "credentials": {
                    "id": str(user.credentials.id),
                    "login": user.credentials.login,
                    "password_hashes": user.credentials.password_hashes,
                    "email": user.credentials.email,
                    "is_admin": user.credentials.is_admin,
                    "is_banned": user.credentials.is_banned,
                },
                "authored_recipes": [str(recipe_id) for recipe_id in user.authored_recipes],
                "recipe_book": {
                    "user_id": str(user.recipe_book.user_id),
                    "entries": {
                        str(entry_id): {
                            "recipe_id": str(entry.recipe_id),
                            "completed_steps": entry.completed_steps,
                            "missing_ingredients": [
                                str(ingredient) for ingredient in entry.missing_ingredients
                            ],
                        }
                        for entry_id, entry in user.recipe_book.entries.items()
                    },
                },
            },
            upsert=True,
        )

    async def get_by_login(self, login: str) -> Optional[User]:
        user_data = await self.collection.find_one({"credentials.login": login})
        if user_data:
            return self._build_user(user_data)
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        user_data = await self.collection.find_one(
            {"credentials.email": email.strip().lower()}
        )
        if user_data:
            return self._build_user(user_data)
        return None

    async def get_all(self) -> List[User]:
        cursor = self.collection.find({}).sort("credentials.login", 1)
        return [self._build_user(user_data) async for user_data in cursor]

    async def delete_user(self, user_id: UUID) -> None:
        await self.collection.delete_one({"_id": str(user_id)})
