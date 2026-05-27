from uuid import UUID
from dataclasses import dataclass


@dataclass
class Rating:
    user_id: UUID
    rating: int
