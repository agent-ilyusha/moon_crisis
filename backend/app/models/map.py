import enum

from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped

from app.models.general import UUID_Mixin
from app.models.Factions import Faction


class LocationType(enum.Enum):
    base = 1
    outpost = 2
    mine = 3
    science_lab = 4


class Map(UUID_Mixin):
    """
    Map model.
    """
    __tablename__ = "maps"

    name: Mapped[String] = Column(String, nullable=False)
    coord_x: Mapped[Float] = Column(Float, nullable=False)
    coord_y: Mapped[Float] = Column(Float, nullable=False)
    location_type: Mapped[Enum] = Column(Enum(LocationType), nullable=False)
    controlling_faction_id:  Mapped[UUID] = Column(ForeignKey(Faction.id), nullable=False)
    has_charging: Mapped[Boolean] = Column(Boolean, nullable=False)

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__dict__.items()])
