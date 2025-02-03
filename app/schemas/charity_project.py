from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field

from app.constants import (
    PROJECT_NAME_FIELD_MAX_LENGTH, PROJECT_NAME_FIELD_MIN_LENGTH,
    PROJECT_DESCRIPTION_FIELD_MIN_LENGTH
)


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=PROJECT_NAME_FIELD_MIN_LENGTH,
        max_length=PROJECT_NAME_FIELD_MAX_LENGTH
    )
    description: Optional[str] = Field(
        None,
        min_length=PROJECT_DESCRIPTION_FIELD_MIN_LENGTH
    )
    full_amount: Optional[int] = Field(None, gt=0)

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(
        ...,
        min_length=PROJECT_NAME_FIELD_MIN_LENGTH,
        max_length=PROJECT_NAME_FIELD_MAX_LENGTH
    )
    description: str = Field(
        ...,
        min_length=PROJECT_DESCRIPTION_FIELD_MIN_LENGTH
    )
    full_amount: int = Field(..., gt=0)


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int = Field(0)
    fully_invested: bool = Field(False)
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True


class CharityProjectUpdate(CharityProjectBase):
    pass
