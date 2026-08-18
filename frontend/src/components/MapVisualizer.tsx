import React, { useState, useMemo, useEffect } from 'react';
import { MapNode, RouteSegment, Rover, RoverStatus } from '../types/game';

interface MapVisualizerProps {
    nodes: MapNode[];
    routes: RouteSegment[];
    rovers: Rover[];
}

const STATUS_COLORS: Record<RoverStatus, string> = {
    idle: '#22c55e',
    en_route: '#eab308',
    charging: '#3b82f6',
    damaged: '#ef4444',
};

export const MapVisualizer: React.FC<MapVisualizerProps> = ({ nodes, routes, rovers }) => {
    const [zoom, setZoom] = useState<number>(1);
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState<boolean>(false);
    const [startDrag, setStartDrag] = useState({ x: 0, y: 0 });
    const containerRef = React.useRef<HTMLDivElement>(null);

    const scaleX = (x: number) => (x + 100) * 4;
    const scaleY = (y: number) => (100 - y) * 4;

    const getCoords = (id: string) => {
        const node = nodes.find((n) => n.id === id);
        return node ? { x: scaleX(node.coord_x), y: scaleY(node.coord_y) } : null;
    };

    const roversByLocation = useMemo(() => {
        const grouped: Record<string, Rover[]> = {};
        for (const rover of rovers) {
            if (!rover.current_location_id) continue;
            if (!grouped[rover.current_location_id]) {
                grouped[rover.current_location_id] = [];
            }
            grouped[rover.current_location_id].push(rover);
        }
        return grouped;
    }, [rovers]);

    // Use passive: false event listener on native ref to strictly prevent default behavior (scroll) in Chrome/Firefox.
    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const handleNativeWheel = (e: WheelEvent) => {
            e.preventDefault();
            e.stopPropagation();
            const factor = e.deltaY > 0 ? 0.85 : 1.15;
            setZoom((prev) => Math.max(0.4, Math.min(prev * factor, 3.5)));
        };

        container.addEventListener('wheel', handleNativeWheel, { passive: false });
        return () => {
            container.removeEventListener('wheel', handleNativeWheel);
        };
    }, []);

    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        setStartDrag({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDragging) return;
        setPan({ x: e.clientX - startDrag.x, y: e.clientY - startDrag.y });
    };

    const size = 800;
    const vWidth = size / zoom;
    const vHeight = size / zoom;
    const vX = (size - vWidth) / 2 - pan.x / zoom;
    const vY = (size - vHeight) / 2 - pan.y / zoom;

    return (
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
                    Карта локаций (Зум: {Math.round(zoom * 100)}%)
                </h2>
                <div style={{ display: 'flex', gap: '6px' }}>
                    <button onClick={() => setZoom(z => Math.min(z + 0.3, 3.5))} style={btnStyle}>+</button>
                    <button onClick={() => setZoom(z => Math.max(z - 0.3, 0.4))} style={btnStyle}>-</button>
                    <button onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }} style={btnStyle}>Сброс</button>
                </div>
            </div>

            <div
                ref={containerRef}
                style={{
                    width: '100%', height: '450px', backgroundColor: '#020617', borderRadius: '4px',
                    overflow: 'hidden', cursor: isDragging ? 'grabbing' : 'grab', touchAction: 'none',
                }}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={() => setIsDragging(false)}
                onMouseLeave={() => setIsDragging(false)}
            >
                <svg width="100%" height="100%" viewBox={`${vX} ${vY} ${vWidth} ${vHeight}`}>
                    {routes.map((r) => {
                        const start = getCoords(r.from_location_id);
                        const end = getCoords(r.to_location_id);
                        if (!start || !end) return null;
                        const isHazardous = (r.hazard_risk ?? 0) > 30;
                        const isVeryHazardous = (r.hazard_risk ?? 0) > 50;
                        const strokeColor = isVeryHazardous ? '#f43f5e' : isHazardous ? '#f59e0b' : '#475569';
                        const strokeWidth = isHazardous ? 3.5 / zoom : 2.0 / zoom;

                        return (
                            <g key={r.id}>
                                <line
                                    x1={start.x}
                                    y1={start.y}
                                    x2={end.x}
                                    y2={end.y}
                                    stroke={strokeColor}
                                    strokeWidth={strokeWidth}
                                    strokeDasharray={isHazardous ? "6,4" : "4,4"}
                                />
                                {/* Hazard % label along the road */}
                                <text
                                    x={(start.x + end.x) / 2}
                                    y={(start.y + end.y) / 2 - 4 / zoom}
                                    fill={strokeColor}
                                    fontSize={10 / zoom}
                                    textAnchor="middle"
                                    style={{ userSelect: 'none', fontWeight: isHazardous ? 'bold' : 'normal' }}
                                >
                                    {r.hazard_risk ? `⚠️ ${r.hazard_risk}%` : ''}
                                </text>
                            </g>
                        );
                    })}

                    {nodes.map((n) => (
                        <g key={n.id}>
                            <circle cx={scaleX(n.coord_x)} cy={scaleY(n.coord_y)} r={10 / zoom} fill="#3b82f6" />
                            <text x={scaleX(n.coord_x)} y={scaleY(n.coord_y) - 16 / zoom} fill="#94a3b8" fontSize={14 / zoom} textAnchor="middle" style={{ pointerEvents: 'none', userSelect: 'none' }}>
                                {n.name}
                            </text>
                        </g>
                    ))}

                    {Object.entries(roversByLocation).flatMap(([locationId, locationRovers]) => {
                        const pos = getCoords(locationId);
                        if (!pos) return [];

                        return locationRovers.map((rover, idx) => {
                            const isEnRoute = rover.status === 'en_route';
                            const color = STATUS_COLORS[rover.status] || STATUS_COLORS.idle;
                            const rSize = 18 / zoom;
                            const totalWidth = locationRovers.length * (rSize + 4) - 4;
                            const offsetX = pos.x + idx * (rSize + 4) - totalWidth / 2 + rSize / 2;

                            return (
                                <g key={rover.id}>
                                    <rect
                                        x={offsetX - rSize / 2}
                                        y={pos.y + 10 / zoom}
                                        width={rSize}
                                        height={rSize}
                                        fill={color}
                                        rx={3 / zoom}
                                    >
                                        {isEnRoute && (
                                            <animate attributeName="opacity" values="1;0.3;1" dur="1s" repeatCount="indefinite" />
                                        )}
                                    </rect>
                                    <text
                                        x={offsetX}
                                        y={pos.y + 38 / zoom}
                                        fill={color}
                                        fontSize={12 / zoom}
                                        textAnchor="middle"
                                        style={{ pointerEvents: 'none', userSelect: 'none', fontWeight: 'bold' }}
                                    >
                                        {rover.name}
                                    </text>
                                    {isEnRoute && (
                                        <text
                                            x={offsetX}
                                            y={pos.y + 52 / zoom}
                                            fill="#fde047"
                                            fontSize={10 / zoom}
                                            textAnchor="middle"
                                            style={{ pointerEvents: 'none', userSelect: 'none' }}
                                        >
                                            Прибывает... ⌛
                                        </text>
                                    )}
                                </g>
                            );
                        });
                    })}
                </svg>
            </div>
        </div>
    );
};

const btnStyle = { padding: '4px 10px', backgroundColor: '#334155', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' };
