from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional, List


class RoverStatus(str, Enum):
    idle = "idle"
    en_route = "en_route"
    charging = "charging"
    damaged = "damaged"


class FactionBase(BaseModel):
    name: str
    tag: str
    description: str


class FactionResponse(FactionBase):
    id: UUID
    reputation: int = 50
    model_config = ConfigDict(from_attributes=True)


class FactionRelationshipCreate(BaseModel):
    first_faction_id: UUID
    second_faction_id: UUID
    reputation_impact: float


class FactionRelationshipUpdate(BaseModel):
    reputation_impact: float


class FactionRelationshipResponse(BaseModel):
    id: UUID
    first_faction_id: UUID
    second_faction_id: UUID
    reputation_impact: float
    model_config = ConfigDict(from_attributes=True)


class StationFactionRepInfo(BaseModel):
    faction_id: UUID
    faction_name: str
    faction_tag: str
    reputation: int
    is_critical: bool  # True if reputation < 20


class StationStatsResponse(BaseModel):
    id: UUID
    name: str
    balance: int
    reputation: int
    fleet_capacity: int
    rovers_count: int
    is_game_over: bool
    game_over_reason: Optional[str] = None
    faction_reputations: List[StationFactionRepInfo] = []


class StationBase(BaseModel):
    name: str
    balance: int = 0
    reputation: int = 0
    fleet_capacity: int = 0


class StationCreate(StationBase):
    user_id: Optional[UUID] = None
    factions: UUID


class StationResponse(StationBase):
    id: UUID
    user_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


class RoverBase(BaseModel):
    name: str
    model: str
    max_payload: int
    battery_capacity: int
    base_drain_rate: int
    armor: int
    now_battery_capacity: int
    position_x: float
    position_y: float
    status: str
    wear: int
    station_id: Optional[UUID] = None


class RoverCreate(RoverBase):
    pass


class RoverUpdate(BaseModel):
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    status: Optional[str] = None
    now_battery_capacity: Optional[int] = None
    wear: Optional[int] = None


class RoverResponse(RoverBase):
    id: UUID
    current_location_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)


class RoverCatalogItem(BaseModel):
    model: str
    name_prefix: str
    price: int
    max_payload: int
    battery_capacity: int
    base_drain_rate: int
    armor: int
    description: str


class RoverBuyRequest(BaseModel):
    model: str
    name: Optional[str] = None


class RoverRepairResponse(BaseModel):
    rover: RoverResponse
    cost_credits: int
    new_station_balance: int
    repaired_wear: int


class MapNodeResponse(BaseModel):
    id: UUID
    name: str
    coord_x: float
    coord_y: float
    location_type: Optional[str] = None
    controlling_faction_id: Optional[UUID] = None
    faction_id: Optional[UUID] = None
    has_charging: bool = True

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_map(cls, map_obj):
        loc_type = (
            map_obj.location_type.name
            if hasattr(map_obj.location_type, "name")
            else str(map_obj.location_type)
        )
        return cls(
            id=map_obj.id,
            name=map_obj.name,
            coord_x=map_obj.coord_x,
            coord_y=map_obj.coord_y,
            location_type=loc_type,
            controlling_faction_id=map_obj.controlling_faction_id,
            faction_id=map_obj.controlling_faction_id,
            has_charging=getattr(map_obj, "has_charging", True),
        )


class RouteResponse(BaseModel):
    id: UUID
    from_location_id: UUID
    to_location_id: UUID
    distance_km: float
    hazard_risk: int = 0
    base_energy_cost: int = 10

    model_config = ConfigDict(from_attributes=True)
