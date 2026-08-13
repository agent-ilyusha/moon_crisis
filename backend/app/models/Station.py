from typing import List

from pydantic import ValidationError
from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import validates, Mapped, relationship

from app.models.Factions import Faction
from app.models.general import UUID_Mixin
from app.models.Rover import Rover
from app.models.User import User


class Station(UUID_Mixin):
    """
    Station model.
    """
    __tablename__ = 'station'

    name: Mapped[String] = Column(String(50), nullable=False, unique=True)
    balance: Mapped[Integer] = Column(Integer, default=0, nullable=False)
    reputation: Mapped[Integer] = Column(Integer, default=0, nullable=False)
    fleet_capacity: Mapped[Integer] = Column(Integer, default=0, nullable=False)

    user_id: Mapped[UUID] = Column(ForeignKey(User.id, ondelete='CASCADE'), nullable=True)
    owner: Mapped[User] = relationship(User, back_populates='stations')
    rovers: Mapped[List[Rover]] = relationship(Rover, back_populates='station')
    factions: Mapped[UUID] = Column(ForeignKey(Faction.id, ondelete='CASCADE'), nullable=False)

    @validates('balance', 'reputation', 'fleet_capacity')
    def validate_balance(self, key: str, value: int):
        if value < 0:
            raise ValidationError()
        return value

    def __str__(self):
        return (f'Название: {self.name}, баланс: {self.balance},'
                f'репутация: {self.reputation}, количество роверов: {self.fleet_capacity}.')

    def __repr__(self):
        return {
            'name': self.name,
            'balance': self.balance,
            'reputation': self.reputation,
            'fleet_capacity': self.fleet_capacity
        }

    class Meta:
        verbose_name = 'Station'
        verbose_name_plural = 'Stations'
