from datetime import datetime
from typing import Literal

from pydantic import EmailStr

from app.schemas.common import ORMModel


class UserRead(ORMModel):
    id: int
    email: EmailStr
    role: Literal["student", "teacher"]
    created_at: datetime
