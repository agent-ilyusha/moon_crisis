import heapq
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.route import RouteSegment
from app.models.rover import Rover


def calculate_server_route(db: Session, start_id: UUID, target_id: UUID):
    """
    Calculate server route.

    Args:
        db: Session database.
        start_id: Start station.
        target_id: End station.

    Return:
        Find route.

    Raises:
        HTTPException: If not path.
    """
    routes = db.query(RouteSegment).all()
    graph = {}

    for r in routes:
        graph.setdefault(r.from_location_id, []).append((r.to_location_id, r.base_energy_cost, r.distance_km))
        graph.setdefault(r.to_location_id, []).append((r.from_location_id, r.base_energy_cost, r.distance_km))

    queue = [(0, id(start_id), start_id, [])]
    visited = set()

    while queue:
        (cost, _, current, path) = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)
        current_path = path + [current]

        if current == target_id:
            return cost, current_path

        for neighbor, edge_cost, _ in graph.get(current, []):
            if neighbor not in visited:
                heapq.heappush(queue, (cost + edge_cost, id(neighbor), neighbor, current_path))

    raise HTTPException(status_code=400, detail="Маршрут заблокирован или не существует!")


def dispatch_rover_secure(db: Session, rover_id: UUID, target_location_id: UUID, cargo_weight: int):
    """
    Dispatch rover secure.

    Args:
        db: Session database.
        rover_id: Id of rover.
        target_location_id: Id of target location.
        cargo_weight: Weight of cargo.

    Return:
        Dictionary of status.

    Raises:
        HTTPException:  If not rover or rover.status != "idle" or not rover.current_location_id
        or cargo_weight > rover.max_payload or rover.now_battery_capacity < total_energy
    """
    rover = db.query(Rover).filter(Rover.id == rover_id).with_for_update().first()

    if not rover:
        raise HTTPException(404, "Ровер не найден")
    if rover.status != "idle":
        raise HTTPException(400, "Ровер недоступен для отправки")
    if not rover.current_location_id:
        raise HTTPException(400, "Ровер не привязан к стартовой локации")
    if cargo_weight > rover.max_payload:
        raise HTTPException(400, "Перегруз! Превышен лимит массы")

    base_energy, path = calculate_server_route(db, rover.current_location_id, target_location_id)
    weight_modifier = 1.0 + (cargo_weight / rover.max_payload)
    total_energy = int(base_energy * weight_modifier)

    if rover.now_battery_capacity < total_energy:
        raise HTTPException(400, f"Нехватка заряда! Нужно: {total_energy}%, Есть: {rover.now_battery_capacity}%")

    rover.now_battery_capacity -= total_energy
    rover.current_location_id = target_location_id
    rover.status = "idle"

    db.commit()
    db.refresh(rover)

    return {
        "status": "success",
        "energy_spent": total_energy,
        "new_location_id": str(target_location_id),
        "path": [str(nid) for nid in path]
    }