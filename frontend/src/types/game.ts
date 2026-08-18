export type RoverStatus = 'idle' | 'en_route' | 'charging' | 'damaged';

export interface MapNode {
  id: string;
  name: string;
  coord_x: number;
  coord_y: number;
  faction_id?: string;
  controlling_faction_id?: string;
  location_type?: string;
  has_charging?: boolean;
}

export interface RouteSegment {
  id: string;
  from_location_id: string;
  to_location_id: string;
  distance_km: number;
  base_energy_cost?: number;
  hazard_risk?: number;
}

export interface Rover {
  id: string;
  name: string;
  model: string;
  max_payload: number;
  battery_capacity: number;
  now_battery_capacity: number;
  status: RoverStatus;
  wear: number;
  armor: number;
  base_drain_rate?: number;
  current_location_id: string;
  station_id?: string;
}

export interface Faction {
  id: string;
  name: string;
  description: string;
  tag?: string;
  reputation?: number;
}

export interface StationFactionRepInfo {
  faction_id: string;
  faction_name: string;
  faction_tag: string;
  reputation: number;
  is_critical: boolean;
}

export interface StationStats {
  id: string;
  name: string;
  balance: number;
  reputation: number;
  fleet_capacity: number;
  rovers_count: number;
  is_game_over: boolean;
  game_over_reason?: string | null;
  faction_reputations: StationFactionRepInfo[];
}

export interface RoverCatalogItem {
  model: string;
  name_prefix: string;
  price: number;
  max_payload: number;
  battery_capacity: number;
  base_drain_rate: number;
  armor: number;
  description: string;
}

export interface DispatchResponse {
  status: string;
  energy_spent: number;
  travel_time_seconds: number;
  hazard_risk?: number;
  wear_inflicted?: number;
  reward_credits?: number;
  reward_rep?: number;
  rover: Rover;
}

export type MapLocation = MapNode;
