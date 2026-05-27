from dataclasses import dataclass
from typing import Dict
from uuid import UUID
from Domain.Entities.RecipeBook.BookEntry import BookEntry

@dataclass
class Book:
    user_id: UUID
    entries: Dict[UUID, BookEntry]