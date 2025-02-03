from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import BaseDonation


class Donation(BaseDonation):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
