from typing import List, Optional
from pydantic import ValidationError
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Mapped, validates, relationship

from app.models.general import UUID_Mixin
from app.models.Station import Station
from app.models.Storage import Storage


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
    storage: Mapped[Optional[Storage]] = relationship(back_populates="storage", cascade="all, delete-orphan")

    def __repr__(self):
        return {
            'name': self.username,
            'role': self.role,
            'station': self.stations,
        }

    def __str__(self):
        return f"Имя: {self.username}, роль: {self.role}, ранг: {self.rank}, станции: {self.stations}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
