import { RouteSegment } from '../types/game';

interface PathResult {
  path: string[];
  totalEnergy: number;
  totalDistance: number;
}

export function findShortestPath(
  locationsIds: string[],
  routes: RouteSegment[],
  startId: string,
  targetId: string
): PathResult | null {
  const distances: Record<string, number> = {};
  const previous: Record<string, string | null> = {};
  const nodes = new Set<string>();

  locationsIds.forEach(id => {
    distances[id] = Infinity;
    previous[id] = null;
    nodes.add(id);
  });

  distances[startId] = 0;

  while (nodes.size > 0) {
    let smallest = Array.from(nodes).reduce((minNode, node) =>
      distances[node] < distances[minNode] ? node : minNode, Array.from(nodes)[0]);

    if (smallest === targetId) {
      const path: string[] = [];
      let curr: string | null = targetId;
      let totalDist = 0;

      while (curr) {
        path.unshift(curr);
        const prev = previous[curr];
        if (prev) {
          const edge = routes.find(r =>
            (r.from_location_id === prev && r.to_location_id === curr) ||
            (r.from_location_id === curr && r.to_location_id === prev)
          );
          if (edge) totalDist += edge.distance_km;
        }
        curr = previous[curr];
      }

      return { path, totalEnergy: distances[targetId], totalDistance: totalDist };
    }

    if (distances[smallest] === Infinity) break;

    nodes.delete(smallest);

    // Находим всех соседей
    const neighbors = routes.filter(
      r => r.from_location_id === smallest || r.to_location_id === smallest
    );

    for (const edge of neighbors) {
      const neighborId = edge.from_location_id === smallest ? edge.to_location_id : edge.from_location_id;
      if (nodes.has(neighborId)) {
        const alt = distances[smallest] + (edge.base_energy_cost ?? 1.0);
        if (alt < distances[neighborId]) {
          distances[neighborId] = alt;
          previous[neighborId] = smallest;
        }
      }
    }
  }

  return null;
}
