from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4


@dataclass
class Comment:
    recipe_id: UUID
    user_id: UUID
    text: str
    image_urls: List[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
