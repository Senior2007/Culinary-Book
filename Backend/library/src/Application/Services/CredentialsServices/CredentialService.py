import hashlib
import os
import re
from uuid import uuid4, UUID
from typing import List
from datetime import datetime, timedelta

from jose import jwt, JWTError

from Domain.Entities.User.User import User
from Domain.Entities.RecipeBook.RecipeBook import Book
from Domain.Entities.User.Credentials import Credentials
from Application.Interfaces.IUserRepository import IUserRepository

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CredentialsService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _check_password(self, password: str, password_hashes: List[str]) -> bool:
        return self._hash_password(password) in password_hashes

    @staticmethod
    def validate_email(email: str) -> str:
        email = email.strip().lower()
        if not email or not EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email address")
        return email

    @staticmethod
    def validate_password_strength(password: str) -> None:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")

    async def register(self, login: str, password: str, email: str) -> UUID:
        login = login.strip()
        if len(login) < 3:
            raise ValueError("Login must be at least 3 characters long")

        email = self.validate_email(email)
        self.validate_password_strength(password)

        if await self.user_repo.get_by_login(login):
            raise ValueError("User with this login already exists")
        if await self.user_repo.get_by_email(email):
            raise ValueError("User with this email already exists")

        new_id = uuid4()
        password_hash = self._hash_password(password)

        credentials = Credentials(
            id=new_id,
            login=login,
            password_hashes=[password_hash],
            email=email,
        )

        new_user = User(
            credentials=credentials,
            authored_recipes=[],
            recipe_book=Book(user_id=new_id, entries={}),
        )

        await self.user_repo.save(new_user)
        return new_id

    async def authenticate(self, login: str, password: str) -> UUID:
        user = await self.user_repo.get_by_login(login)
        if user is None:
            raise ValueError("User with this login not found")

        if not self._check_password(password, user.credentials.password_hashes):
            raise ValueError("Wrong password")

        return user.credentials.id

    def generate_token(self, user_id: UUID) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def validate_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Invalid token")
            return UUID(user_id)
        except (JWTError, ValueError):
            raise ValueError("Invalid or expired token")
