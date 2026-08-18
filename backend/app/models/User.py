from typing import List
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Mapped, relationship

from app.models.general import UUID_Mixin
from app.models.Station import Station


class User(UUID_Mixin):
    """
    User model.
    """
    __tablename__ = 'users'

    username: Mapped[String] = Column(String(50), nullable=False)
    hashed_password: Mapped[String] = Column(String(150), nullable=False)
    role: Mapped[String] = Column(String(30), nullable=False)
    created_at: Mapped[DateTime] = Column(DateTime, nullable=False)

    stations: Mapped[List[Station]] = relationship(back_populates='owner', cascade='all, delete-orphan')

    def __str__(self):
        return f"Имя: {self.username}, роль: {self.role}, станции: {self.stations}"
