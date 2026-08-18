from sqlalchemy import Column, Integer, Float, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, validates, relationship
from app.models.general import UUIDMixin


class Rover(UUIDMixin):
    __tablename__ = 'rover'

    name: Mapped[String] = Column(String(50), nullable=False, unique=True)
    model: Mapped[String] = Column(String(50), nullable=False)  # Исправлена опечатка
    max_payload: Mapped[Integer] = Column(Integer, nullable=False)
    battery_capacity: Mapped[Integer] = Column(Integer, nullable=False)  # Абсолютная емкость
    base_drain_rate: Mapped[Integer] = Column(Integer, nullable=False)
    armor: Mapped[Integer] = Column(Integer, nullable=False)

    now_battery_capacity: Mapped[Integer] = Column(Integer, nullable=False)  # % заряда (0-100)
    position_x: Mapped[Float] = Column(Float, nullable=False, default=0.0)
    position_y: Mapped[Float] = Column(Float, nullable=False, default=0.0)
    status: Mapped[String] = Column(String, nullable=False, default="idle")
    wear: Mapped[Integer] = Column(Integer, nullable=False, default=0)

    current_location_id: Mapped[UUID] = Column(ForeignKey('maps.id'), nullable=True)
    station_id: Mapped[UUID] = Column(ForeignKey('station.id'), nullable=True)
    station_owner: Mapped["Station"] = relationship("Station", back_populates='rovers')

    @validates('now_battery_capacity', 'wear')
    def validate_percentages(self, key, value):
        if not (0 <= value <= 100):
            raise ValueError(f'{key} must be between 0 and 100%.')
        return value
