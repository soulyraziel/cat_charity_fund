from sqlalchemy import Column, String, Text

from app.constants import PROJECT_NAME_FIELD_MAX_LENGTH
from app.models.base import BaseDonation


class CharityProject(BaseDonation):
    name = Column(String(PROJECT_NAME_FIELD_MAX_LENGTH), unique=True,
                  nullable=False)
    description = Column(Text, nullable=False)
