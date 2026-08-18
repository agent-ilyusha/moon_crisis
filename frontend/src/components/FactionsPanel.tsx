import React, { useEffect, useState } from 'react';
import { Faction, StationFactionRepInfo } from '../types/game';
import { API_BASE } from '../config';

interface FactionsPanelProps {
    factions?: StationFactionRepInfo[];
    onRefresh?: () => void;
}

export const FactionsPanel: React.FC<FactionsPanelProps> = ({ factions: propsFactions }) => {
    const [fetchedFactions, setFetchedFactions] = useState<Faction[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!propsFactions) {
            setLoading(true);
            fetch(`${API_BASE}/factions`)
                .then((res) => res.json())
                .then((data) => setFetchedFactions(data))
                .catch((err) => console.error('Ошибка загрузки фракций:', err))
                .finally(() => setLoading(false));
        }
    }, [propsFactions]);

    const displayFactions = propsFactions || fetchedFactions.map(f => ({
        faction_id: f.id,
        faction_name: f.name,
        faction_tag: f.tag || '',
        reputation: f.reputation ?? 50,
        is_critical: (f.reputation ?? 50) < 20,
    }));

    return (
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '16px', marginTop: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
                    Лунное содружество (Отношения и Репутация фракций)
                </h2>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {'Порог поражения: < 20 очков'}
                </span>
            </div>

            {loading ? (
                <div style={{ color: '#94a3b8', fontSize: '14px' }}>Загрузка данных фракций...</div>
            ) : displayFactions.length === 0 ? (
                <div style={{ color: '#64748b', fontSize: '14px' }}>Фракции не найдены</div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
                    {displayFactions.map((f) => {
                        const rep = f.reputation;
                        const isCritical = rep < 20;
                        const barColor = isCritical ? '#ef4444' : rep < 40 ? '#f59e0b' : rep < 70 ? '#38bdf8' : '#22c55e';

                        return (
                            <div
                                key={f.faction_id}
                                style={{
                                    backgroundColor: '#0f172a',
                                    border: `1px solid ${isCritical ? '#ef4444' : '#334155'}`,
                                    padding: '14px',
                                    borderRadius: '6px',
                                    boxShadow: isCritical ? '0 0 12px rgba(239, 68, 68, 0.3)' : 'none',
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                                    <div style={{ fontWeight: 700, color: '#38bdf8', fontSize: '14px' }}>
                                        {f.faction_name} {f.faction_tag ? `[${f.faction_tag}]` : ''}
                                    </div>
                                    <div style={{ fontWeight: 700, color: barColor, fontSize: '15px' }}>
                                        {rep} <span style={{ fontSize: '11px', color: '#94a3b8' }}>/ 100</span>
                                    </div>
                                </div>

                                {/* Reputation Progress Bar */}
                                <div style={{ width: '100%', height: '8px', backgroundColor: '#334155', borderRadius: '4px', overflow: 'hidden', margin: '8px 0', position: 'relative' }}>
                                    <div
                                        style={{
                                            width: `${Math.max(0, Math.min(100, rep))}%`,
                                            height: '100%',
                                            backgroundColor: barColor,
                                            transition: 'width 0.5s ease',
                                        }}
                                    />
                                    {/* Critical threshold mark at 20% */}
                                    <div
                                        style={{
                                            position: 'absolute',
                                            left: '20%',
                                            top: 0,
                                            bottom: 0,
                                            width: '2px',
                                            backgroundColor: '#ef4444',
                                            zIndex: 2,
                                        }}
                                        title="Критический порог 20"
                                    />
                                </div>

                                {isCritical ? (
                                    <div style={{ color: '#f87171', fontSize: '12px', fontWeight: 600, marginTop: '4px' }}>
                                        ⚠️ КРИТИЧЕСКИ НИЗКАЯ РЕПУТАЦИЯ {'(< 20)'}!
                                    </div>
                                ) : (
                                    <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>
                                        {rep >= 70 ? '🟢 Союзнические отношения' : rep >= 40 ? '🔵 Нейтральный статус' : '🟡 Напряжённые отношения'}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};
