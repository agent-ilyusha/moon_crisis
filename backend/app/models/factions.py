import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.general import UUIDMixin


class Faction(UUIDMixin):
    """
    Faction model.
    """
    __tablename__ = 'factions'

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__dict__.items()])


class Factions_relationship(UUIDMixin):
    """
    Factions_relationship model.
    """
    __tablename__ = 'factions_relationship'

    reputation_impact: Mapped[float] = mapped_column(Float, nullable=False)
    first_faction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('factions.id'), nullable=False)
    second_faction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('factions.id'), nullable=False)

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__dict__.items()])


class Station_faction_reputation(UUIDMixin):
    """
    Station_faction_reputation model.
    """
    __tablename__ = 'station_faction_reputation'

    station_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('station.id'), nullable=False)
    faction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('factions.id'), nullable=False)
    reputation: Mapped[int] = mapped_column(Integer, nullable=False)

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__dict__.items()])
