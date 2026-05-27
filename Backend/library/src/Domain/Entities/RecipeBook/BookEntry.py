from dataclasses import dataclass
from typing import List
from uuid import UUID


@dataclass
class BookEntry:
    recipe_id: UUID
    completed_steps: List[int]
    missing_ingredients: List[str]