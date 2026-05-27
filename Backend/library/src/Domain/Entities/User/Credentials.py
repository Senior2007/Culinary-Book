from uuid import UUID
from dataclasses import dataclass
from typing import List

@dataclass
class Credentials:
    id: UUID
    login: str
    password_hashes: List[str]
    email: str = ""
    is_admin: bool = False
    is_banned: bool = False
