from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass

from Domain.Entities.Recipe.Tag import Tag
from Domain.Entities.Recipe.Step import Step
from Domain.Entities.Recipe.Ingredient import Ingredient


@dataclass
class Recipe:
    id: UUID
    title: str
    author_id: UUID
    ingredients: List[Ingredient]
    steps: List[Step]
    tags: List[Tag]
    is_published: bool
    cover_url: Optional[str] = None