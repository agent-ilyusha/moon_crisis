
from sqlalchemy import UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship, validates

from app.models import Rover, User
from app.models.general import UUIDMixin


class Station(UUIDMixin):
    __tablename__ = 'station'

    name: Mapped[String] = Column(String(50), nullable=False, unique=True)
    balance: Mapped[Integer] = Column(Integer, default=0, nullable=False)
    reputation: Mapped[Integer] = Column(Integer, default=0, nullable=False)
    fleet_capacity: Mapped[Integer] = Column(Integer, default=0, nullable=False)

    location_id: Mapped[UUID] = Column(ForeignKey('maps.id', ondelete='SET NULL'), nullable=True)

    user_id: Mapped[UUID] = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    faction_id: Mapped[UUID] = Column(ForeignKey('factions.id', ondelete='CASCADE'), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates='stations')
    rovers: Mapped[list["Rover"]] = relationship("Rover", back_populates='station_owner')

    @validates('balance', 'reputation', 'fleet_capacity')
    def validate_non_negative(self, key: str, value: int):
        if value < 0:
            raise ValueError(f'{key} must be greater than or equal to zero')
        return value
