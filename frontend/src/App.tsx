import React, { useState, useEffect, useCallback } from 'react';
import { Rover, MapNode, RouteSegment, StationStats } from './types/game';
import { MapVisualizer } from './components/MapVisualizer';
import { RoverControlCenter } from './components/RoverControlCenter';
import { FactionsPanel } from './components/FactionsPanel';
import { API_BASE } from './config';

export default function App() {
  const [rovers, setRovers] = useState<Rover[]>([]);
  const [nodes, setNodes] = useState<MapNode[]>([]);
  const [routes, setRoutes] = useState<RouteSegment[]>([]);
  const [stationStats, setStationStats] = useState<StationStats | null>(null);

  const refreshData = useCallback(async () => {
    try {
      const [roversRes, nodesRes, routesRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/rovers`),
        fetch(`${API_BASE}/nodes`),
        fetch(`${API_BASE}/routes`),
        fetch(`${API_BASE}/stations/stats`),
      ]);
      if (roversRes.ok && nodesRes.ok && routesRes.ok) {
        setRovers(await roversRes.json());
        setNodes(await nodesRes.json());
        setRoutes(await routesRes.json());
      }
      if (statsRes.ok) {
        setStationStats(await statsRes.json());
      }
    } catch (error) {
      console.error('Ошибка загрузки данных системы:', error);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  useEffect(() => {
    const hasEnRoute = rovers.some((r) => r.status === 'en_route');
    const intervalTime = hasEnRoute ? 1500 : 4000;

    const interval = setInterval(refreshData, intervalTime);
    return () => clearInterval(interval);
  }, [rovers, refreshData]);

  const handleResetGame = async () => {
    try {
      const res = await fetch(`${API_BASE}/stations/reset`, { method: 'POST' });
      if (res.ok) {
        await refreshData();
      }
    } catch (e) {
      console.error('Ошибка сброса игры:', e);
    }
  };

  const isGameOver = stationStats?.is_game_over ?? false;

  return (
    <div
      style={{
        padding: '24px',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        color: '#e2e8f0',
        backgroundColor: '#0f172a',
        minHeight: '100vh',
        boxSizing: 'border-box',
      }}
    >
      {/* Game Over Banner */}
      {isGameOver && (
        <div
          style={{
            backgroundColor: '#7f1d1d',
            border: '2px solid #ef4444',
            borderRadius: '8px',
            padding: '16px 20px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 10px 25px rgba(239, 68, 68, 0.4)',
          }}
        >
          <div>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#fef2f2', marginBottom: '4px' }}>
              💀 ПОРАЖЕНИЕ (GAME OVER)
            </div>
            <div style={{ fontSize: '14px', color: '#fecaca' }}>
              {stationStats?.game_over_reason || 'Репутация с одной из фракций упала ниже критического порога (20)!'}
            </div>
          </div>
          <button
            onClick={handleResetGame}
            style={{
              padding: '10px 20px',
              backgroundColor: '#ef4444',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 700,
              cursor: 'pointer',
              fontSize: '14px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            }}
          >
            🔄 Начать заново
          </button>
        </div>
      )}

      {/* Header & Objectives */}
      <header
        style={{
          marginBottom: '24px',
          borderBottom: '1px solid #334155',
          paddingBottom: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
            Moon Rover Control Center
          </h1>
          <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Центр управления лунной логистической сетью
          </p>
          <div
            style={{
              marginTop: '10px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#1e293b',
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid #3b82f6',
              fontSize: '13px',
              color: '#93c5fd',
            }}
          >
            <span>🎯 <strong>Цель игры:</strong> Балансировать интересы фракций и не опустить репутацию ни с одной ниже <strong>20</strong>!</span>
          </div>
        </div>

        {/* Station Financial & Fleet Stats Bar */}
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <div
            style={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              padding: '10px 16px',
              borderRadius: '8px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Баланс станции
            </div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: '#4ade80', marginTop: '2px' }}>
              💰 {stationStats ? stationStats.balance.toLocaleString() : '—'} <span style={{ fontSize: '12px' }}>CR</span>
            </div>
          </div>

          <div
            style={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              padding: '10px 16px',
              borderRadius: '8px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Суммарная репутация
            </div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: '#38bdf8', marginTop: '2px' }}>
              ⭐ {stationStats ? stationStats.reputation : '—'} <span style={{ fontSize: '12px' }}>pts</span>
            </div>
          </div>

          <div
            style={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              padding: '10px 16px',
              borderRadius: '8px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Флот роверов
            </div>
            <div style={{ fontSize: '20px', fontWeight: 700, color: '#f59e0b', marginTop: '2px' }}>
              🤖 {stationStats ? `${stationStats.rovers_count}/${stationStats.fleet_capacity}` : '—'}
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <MapVisualizer nodes={nodes} routes={routes} rovers={rovers} />
        <RoverControlCenter
          rovers={rovers}
          nodes={nodes}
          routes={routes}
          stationBalance={stationStats?.balance ?? 0}
          isGameOver={isGameOver}
          onMissionComplete={refreshData}
        />
      </div>

      <FactionsPanel factions={stationStats?.faction_reputations} onRefresh={refreshData} />
    </div>
  );
}
