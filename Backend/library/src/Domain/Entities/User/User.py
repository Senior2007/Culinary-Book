from typing import List
from uuid import UUID
from dataclasses import dataclass
from Domain.Entities.RecipeBook.RecipeBook import Book
from Domain.Entities.User.Credentials import Credentials

@dataclass
class User:
    credentials: Credentials
    authored_recipes: List[UUID]
    recipe_book: Book
