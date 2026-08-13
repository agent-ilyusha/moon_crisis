from typing import List
from sqlalchemy import Column, ForeignKey, UUID
from sqlalchemy.orm import Mapped, relationship

from app.models.general import UUID_Mixin
from app.models.Rover import Rover
from app.models.User import User


class Storage(UUID_Mixin):
    """
    Storage model.
    """
    __tablename__ = 'storage'

    user_id: Mapped[UUID] = Column(ForeignKey(User.id, ondelete='CASCADE'), unique=True, nullable=False)
    user: Mapped[User] = relationship(User, back_populates='storage')
    rovers: Mapped[List[Rover]] = relationship(Rover, back_populates='storage')

    class Meta:
        verbose_name = 'Storage'
        verbose_name_plural = 'Storages'
