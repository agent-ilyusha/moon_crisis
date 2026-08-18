from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.general import UUIDMixin
from app.models.station import Station


class User(UUIDMixin):
    """
    User model.
    """
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    stations: Mapped[list[Station]] = relationship(back_populates='owner', cascade='all, delete-orphan')

    def __str__(self):
        return f"Имя: {self.username}, роль: {self.role}, станции: {self.stations}"