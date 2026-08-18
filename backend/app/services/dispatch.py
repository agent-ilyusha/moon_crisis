import heapq
import time
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import Session as SessionFactory
from app.models.factions import (
    Factions_relationship,
    Station_faction_reputation,
)
from app.models.map import Map
from app.models.route import RouteSegment
from app.models.rover import Rover
from app.models.station import Station


def find_route_distance_km(db: Session, start_id: UUID, target_id: UUID) -> float:
    """
    Compatibility with the old call.

    Args:
        db: Session database.
        start_id: Start location.
        target_id: End location.

    Return:
        Distance between start and end.
    """
    distance, _, _ = find_route_info(db, start_id, target_id)
    return distance


def find_route_info(
    db: Session, start_id: UUID, target_id: UUID
) -> tuple[float, float, list[UUID]]:
    """
    Find route info.

    Args:
        db: Session database.
        start_id: Start location.
        target_id: End location.

    Return:
        Finds the shortest path, total distance (km), and average hazard risk of the zone.

    Raises:
        HTTPException: If not path.
    """
    if start_id == target_id:
        return 0.0, 0.0, [start_id]

    routes = db.query(RouteSegment).all()
    graph: dict[UUID, list[tuple[UUID, float, int]]] = {}
    for route in routes:
        graph.setdefault(route.from_location_id, []).append(
            (route.to_location_id, route.distance_km, route.hazard_risk or 0)
        )
        graph.setdefault(route.to_location_id, []).append(
            (route.from_location_id, route.distance_km, route.hazard_risk or 0)
        )

    queue: list[tuple[float, int, UUID, list[UUID], float, int]] = [
        (0.0, id(start_id), start_id, [start_id], 0.0, 0)
    ]
    visited: set[UUID] = set()

    while queue:
        distance, _, current, path, total_hazard, edge_count = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)

        if current == target_id:
            avg_hazard = (total_hazard / edge_count) if edge_count > 0 else 0.0
            return distance, avg_hazard, path

        for neighbor, edge_distance, edge_hazard in graph.get(current, []):
            if neighbor not in visited:
                heapq.heappush(
                    queue,
                    (
                        distance + edge_distance,
                        id(neighbor),
                        neighbor,
                        path + [neighbor],
                        total_hazard + edge_hazard,
                        edge_count + 1,
                    ),
                )

    raise HTTPException(status_code=400, detail="Маршрут между локациями не найден")


def calculate_travel_time_seconds(distance_km: float, hazard_risk: float = 0.0) -> int:
    """
    Calculate travel time seconds.

    Args:
        distance_km: All distance.
        hazard_risk: Risk for rover.

    Return:
        Time for travel.
    """
    hazard_slowdown = 1.0 + (hazard_risk / 50.0)
    return max(5, round(distance_km * 1.5 * hazard_slowdown))


def calculate_energy_spent(
    distance_km: float,
    cargo_mass: float,
    max_payload: float = 500.0,
    hazard_risk: float = 0.0,
) -> float:
    """
    Calculate energy spent.

    Args:
        distance_km: All distance.
        cargo_mass: Mass of cargo.
        max_payload: Max payload rover.
        hazard_risk: Risk for rover.

    Return:
        Energy spent.
    """
    CONSUMPTION_PER_KM = 0.1
    base_cost = distance_km * CONSUMPTION_PER_KM
    cargo_factor = 1.0 + (cargo_mass / max_payload) if max_payload > 0 else 1.0
    hazard_factor = 1.0 + (hazard_risk / 100.0)

    return round(base_cost * cargo_factor * hazard_factor, 1)


def calculate_wear_inflicted(
    distance_km: float,
    cargo_mass: float,
    max_payload: float = 500.0,
    hazard_risk: float = 0.0,
    armor: int = 50,
) -> int:
    """
    Calculate wear inflicted.

    Args:
        distance_km: All distance.
        cargo_mass: Mass of cargo.
        max_payload: Max payload rover.
        hazard_risk: Risk for rover.
        armor: Armor rover.

    Return:
        Inflicted.
    """
    armor_factor = 50.0 / max(10, armor)
    cargo_stress = 1.0 + (cargo_mass / max_payload if max_payload > 0 else 0)
    wear = (distance_km * 0.02 + hazard_risk * 0.2) * cargo_stress * armor_factor
    return max(1, min(100, round(wear)))


def calculate_rewards(
    distance_km: float,
    cargo_mass: float,
    station_faction_id: UUID | None = None,
    target_faction_id: UUID | None = None
) -> tuple[int, float]:
    """
    Calculate rewards.

    Args:
        distance_km: All distance.
        cargo_mass: Mass of cargo.
        station_faction_id: First station id.
        target_faction_id: Second station id.

    Return:
        Rewards.
    """
    earned_credits = int(100 + distance_km * 3.0 + cargo_mass * 1.5)
    
    multiplier = 1.0
    if station_faction_id and target_faction_id and station_faction_id == target_faction_id:
        multiplier = 1.5
        
    earned_rep = round((5.0 + (cargo_mass * 0.02) + (distance_km * 0.01)) * multiplier, 1)
    return earned_credits, earned_rep


def schedule_rover_arrival(
    rover_id: UUID,
    cargo_mass: float,
    travel_time_seconds: int,
    wear_inflicted: int = 0,
    target_location_id: UUID | None = None,
    distance_km: float = 0.0,
) -> None:
    """
    Schedule rover arrival.

    Args:
        rover_id: Id of rover.
        cargo_mass: Mass of cargo.
        travel_time_seconds: Travel time.
        wear_inflicted: Wear inflicted.
        target_location_id: Target location.
        distance_km: Distance.

    Return:
        None.
    """
    time.sleep(travel_time_seconds)

    db = SessionFactory()
    try:
        rover = db.query(Rover).filter(Rover.id == rover_id).first()
        if not rover:
            return

        rover.wear = min(100, rover.wear + wear_inflicted)
        if rover.wear >= 100:
            rover.status = "damaged"
        else:
            rover.status = "idle"

        if target_location_id:
            rover.current_location_id = target_location_id

        station = None
        if rover.station_id:
            station = db.query(Station).filter(Station.id == rover.station_id).first()
        if not station:
            station = db.query(Station).first()

        target_node = (
            db.query(Map).filter(Map.id == rover.current_location_id).first()
            if rover.current_location_id
            else None
        )

        dest_faction_id = (
            target_node.controlling_faction_id
            if target_node and hasattr(target_node, "controlling_faction_id")
            else None
        )

        station_faction_id = station.faction_id if station else None
        earned_credits, earned_rep = calculate_rewards(distance_km, cargo_mass, station_faction_id, dest_faction_id)

        if station:
            station.balance += earned_credits

        if station and dest_faction_id:
            stat_rep = (
                db.query(Station_faction_reputation)
                .filter(
                    Station_faction_reputation.station_id == station.id,
                    Station_faction_reputation.faction_id == dest_faction_id,
                )
                .first()
            )
            if not stat_rep:
                stat_rep = Station_faction_reputation(
                    station_id=station.id,
                    faction_id=dest_faction_id,
                    reputation=50,
                )
                db.add(stat_rep)

            stat_rep.reputation = min(100, stat_rep.reputation + round(earned_rep))

            relationships = (
                db.query(Factions_relationship)
                .filter(
                    (Factions_relationship.first_faction_id == dest_faction_id)
                    | (Factions_relationship.second_faction_id == dest_faction_id)
                )
                .all()
            )

            for rel in relationships:
                rival_id = (
                    rel.second_faction_id
                    if rel.first_faction_id == dest_faction_id
                    else rel.first_faction_id
                )
                rival_rep = (
                    db.query(Station_faction_reputation)
                    .filter(
                        Station_faction_reputation.station_id == station.id,
                        Station_faction_reputation.faction_id == rival_id,
                    )
                    .first()
                )
                if rival_rep:
                    rival_rep.reputation = max(0, rival_rep.reputation + int(round(rel.reputation_impact)))

            all_reps = (
                db.query(Station_faction_reputation)
                .filter(Station_faction_reputation.station_id == station.id)
                .all()
            )
            if all_reps:
                station.reputation = sum(r.reputation for r in all_reps)

        db.commit()
    finally:
        db.close()
