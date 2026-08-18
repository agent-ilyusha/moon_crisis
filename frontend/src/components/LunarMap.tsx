import React from 'react';
import { MapLocation, RouteSegment } from '../types/game';

interface LunarMapProps {
  locations: MapLocation[];
  routes: RouteSegment[];
  selectedStartId: string | null;
  selectedTargetId: string | null;
  highlightedPath: string[];
  onSelectLocation: (id: string) => void;
}

export const LunarMap: React.FC<LunarMapProps> = ({
  locations,
  routes,
  selectedStartId,
  selectedTargetId,
  highlightedPath,
  onSelectLocation,
}) => {
  const getLocation = (id: string) => locations.find(l => l.id === id);

  const isEdgeInPath = (from: string, to: string) => {
    for (let i = 0; i < highlightedPath.length - 1; i++) {
      if (
        (highlightedPath[i] === from && highlightedPath[i + 1] === to) ||
        (highlightedPath[i] === to && highlightedPath[i + 1] === from)
      ) {
        return true;
      }
    }
    return false;
  };

  return (
    <div className="relative w-full h-[600px] bg-slate-950 rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
      <svg className="w-full h-full">
        {/* Градиенты и фильтры для стилизации */}
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* 1. Отрисовка дорог (Ребер графа) */}
        {routes.map(route => {
          const from = getLocation(route.from_location_id);
          const to = getLocation(route.to_location_id);
          if (!from || !to) return null;

          const active = isEdgeInPath(from.id, to.id);
          const isHazardous = route.hazard_risk ?? 0 > 30;

          return (
            <g key={route.id}>
              <line
                x1={from.coord_x}
                y1={from.coord_y}
                x2={to.coord_x}
                y2={to.coord_y}
                stroke={active ? '#3b82f6' : isHazardous ? '#ef4444' : '#334155'}
                strokeWidth={active ? 4 : 2}
                strokeDasharray={isHazardous && !active ? '5,5' : 'none'}
                filter={active ? 'url(#glow)' : undefined}
                className="transition-all duration-300"
              />
              {/* Метка расстояния/риска по центру дороги */}
              <text
                x={(from.coord_x + to.coord_x) / 2}
                y={(from.coord_y + to.coord_y) / 2 - 5}
                fill={isHazardous ? '#fca5a5' : '#64748b'}
                fontSize="10"
                textAnchor="middle"
              >
                {route.distance_km}km {isHazardous && '⚠️'}
              </text>
            </g>
          );
        })}

        {/* 2. Отрисовка станций (Узлов графа) */}
        {locations.map(loc => {
          const isStart = loc.id === selectedStartId;
          const isTarget = loc.id === selectedTargetId;
          const isInPath = highlightedPath.includes(loc.id);

          let nodeColor = '#0284c7'; // default lab/outpost
          if (loc.location_type === 'base') nodeColor = '#10b981';
          if (loc.location_type === 'mine') nodeColor = '#f59e0b';

          return (
            <g
              key={loc.id}
              onClick={() => onSelectLocation(loc.id)}
              className="cursor-pointer group"
            >
              {/* Подсветка активных узлов */}
              {(isStart || isTarget || isInPath) && (
                <circle
                  cx={loc.coord_x}
                  cy={loc.coord_y}
                  r={isStart || isTarget ? 22 : 16}
                  fill={isStart ? '#10b981' : isTarget ? '#ef4444' : '#3b82f6'}
                  opacity="0.3"
                  className="animate-pulse"
                />
              )}

              {/* Основной кружок узла */}
              <circle
                cx={loc.coord_x}
                cy={loc.coord_y}
                r={12}
                fill={nodeColor}
                stroke="#0f172a"
                strokeWidth="2"
                className="group-hover:scale-125 transition-transform duration-200"
              />

              {/* Название локации */}
              <text
                x={loc.coord_x}
                y={loc.coord_y + 25}
                fill="#f8fafc"
                fontSize="12"
                fontWeight="600"
                textAnchor="middle"
                className="pointer-events-none select-none"
              >
                {loc.name}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
