from sqlalchemy import UUID, Column, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped

from app.models.general import UUIDMixin


class RouteSegment(UUIDMixin):
    """
    Route model.
    """
    __tablename__ = 'route_segments'

    from_location_id: Mapped[UUID] = Column(ForeignKey('maps.id'), nullable=False)
    to_location_id: Mapped[UUID] = Column(ForeignKey('maps.id'), nullable=False)
    distance_km: Mapped[Float] = Column(Float, nullable=False)
    hazard_risk: Mapped[Integer] = Column(Integer, default=0, nullable=False)
    base_energy_cost: Mapped[Integer] = Column(Integer, default=10, nullable=False)
