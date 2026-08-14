from sqlalchemy import Column, Integer, Float, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, validates, relationship

from app.models.general import UUID_Mixin
from app.models.Station import Station


class Rover(UUID_Mixin):
    """
    Rover model.
    """
    __tablename__ = 'rover'

    # Static fields
    name: Mapped[String] = Column(String(50), nullable=False, unique=True)
    madel: Mapped[String] = Column(String(50), nullable=False)
    max_payload: Mapped[Integer] = Column(Integer, nullable=False)
    battery_capacity: Mapped[Integer] = Column(Integer, nullable=False)
    base_drain_rate: Mapped[Integer] = Column(Integer, nullable=False)
    armor: Mapped[Integer] = Column(Integer, nullable=False)

    # Dynamic fields
    now_battery_capacity: Mapped[Integer] = Column(Integer, nullable=False)
    position_x: Mapped[Float] = Column(Float, nullable=False)
    position_y: Mapped[Float] = Column(Float, nullable=False)
    status: Mapped[String] = Column(String, nullable=False)
    wear: Mapped[Integer] = Column(Integer, nullable=False)

    # Relationship
    station_id: Mapped[UUID] = Column(ForeignKey(Station.id), nullable=True)
    station_owner: Mapped[Station] = relationship(Station, back_populates='rovers')

    @validates('max_payload', 'base_drain_rate', 'armor')
    def validate_max_payload(self, key, value):
        if value < 0:
            raise ValueError(f'{key} must be greater than or equal to zero.')
        return value

    @validates('battery_capacity', 'wear')
    def validate_battery_capacity(self, key, value):
        if 0 <= value <= 100:
            return value
        raise ValueError(f'{key} capacity must be between 0 and 100.')

    def __str__(self):
        return ', '.join([f'{key}: {val}' for key, val in self.__dict__.items()])
