from pydantic import ValidationError
from sqlalchemy import Column, Integer, Float, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, validates, relationship

from app.models.general import UUID_Mixin
from app.models.Station import Station


class Faction(UUID_Mixin):
    """
    Faction model.
    """
    __tablename__ = 'factions'

    name: Mapped[String] = Column(String(100), nullable=False)
    tag: Mapped[UUID] = Column(String(10), nullable=False)
    description: Mapped[String] = Column(String(500), nullable=False)

    def __repr__(self):
        return {
            'name': self.name,
            'tag': self.tag,
            'description': self.description,
        }

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__repr__().items()])

    class Meta:
        verbose_name = 'Faction'
        verbose_name_plural = 'Factions'


class Factions_relationship(UUID_Mixin):
    """
    Factions_relationship model.
    """
    __tablename__ = 'factions_relationship'

    reputation_impact: Mapped[Float] = Column(Float, nullable=False)
    first_faction_id: Mapped[UUID] = Column(ForeignKey('factions.id'), nullable=False)
    second_faction_id: Mapped[UUID] = Column(ForeignKey('factions.id'), nullable=False)

    def __repr__(self):
        return {
            'reputation_impact': self.reputation_impact,
            'first_faction_id': self.first_faction_id,
            'second_faction_id': self.second_faction_id,
        }

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__repr__().items()])


class Station_faction_reputation(UUID_Mixin):
    """
    Station_faction_reputation model.
    """
    __tablename__ = 'station_faction_reputation'

    station_id: Mapped[UUID] = Column(ForeignKey(Station.id), nullable=False)
    faction_id: Mapped[UUID] = Column(ForeignKey(Faction.id), nullable=False)
    reputation: Mapped[Integer] = Column(Integer, nullable=False)

    def __repr__(self):
        return {
            'station_id': self.station_id,
            'faction_id': self.faction_id,
            'reputation': self.reputation,
        }

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__repr__().items()])

    class Meta:
        verbose_name = 'Station Faction'
        verbose_name_plural = 'Station Factions'
