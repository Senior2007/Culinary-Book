from dataclasses import dataclass
from typing import List
from Domain.Entities.Recipe.RecipeContent import RecipeContent

@dataclass
class Step:
    description: str
    contents: List[RecipeContent]
    