import React, { useState, useEffect, useRef } from 'react';
import { Rover, MapNode, RouteSegment, RoverCatalogItem, DispatchResponse } from '../types/game';
import { API_BASE } from '../config';

interface RoverControlCenterProps {
    rovers: Rover[];
    nodes: MapNode[];
    routes: RouteSegment[];
    stationBalance: number;
    isGameOver: boolean;
    onMissionComplete: () => void;
}

export const RoverControlCenter: React.FC<RoverControlCenterProps> = ({
    rovers,
    nodes,
    routes,
    stationBalance,
    isGameOver,
    onMissionComplete,
}) => {
    const [selectedRoverId, setSelectedRoverId] = useState<string>('');
    const [targetLocationId, setTargetLocationId] = useState<string>('');
    const [cargoWeight, setCargoWeight] = useState<number>(0);
    const [loading, setLoading] = useState<boolean>(false);
    const [logs, setLogs] = useState<string[]>([]);
    const [countdown, setCountdown] = useState<number | null>(null);
    const [error, setError] = useState<string>('');
    const [isShopOpen, setIsShopOpen] = useState<boolean>(false);
    const [catalog, setCatalog] = useState<RoverCatalogItem[]>([]);
    const [shopLoading, setShopLoading] = useState<boolean>(false);
    const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
        if (!selectedRoverId && rovers.length > 0) {
            setSelectedRoverId(rovers[0].id);
        }
    }, [rovers, selectedRoverId]);

    // Загрузка каталога магазина
    useEffect(() => {
        if (isShopOpen) {
            setShopLoading(true);
            fetch(`${API_BASE}/rovers/catalog`)
                .then((r) => r.json())
                .then((data) => setCatalog(data))
                .catch((e) => console.error('Ошибка загрузки каталога:', e))
                .finally(() => setShopLoading(false));
        }
    }, [isShopOpen]);

    // Сбрасываем ошибку при смене ровера, точки назначения или веса
    useEffect(() => {
        setError('');
    }, [selectedRoverId, targetLocationId, cargoWeight]);

    useEffect(() => {
        return () => {
            if (countdownRef.current) clearInterval(countdownRef.current);
        };
    }, []);

    const activeRover = rovers.find((r) => r.id === selectedRoverId) || rovers[0] || null;

    const addLog = (message: string) => {
        const time = new Date().toLocaleTimeString();
        setLogs((prev) => [`[${time}] ${message}`, ...prev]);
    };

    const startCountdown = (seconds: number, roverName: string) => {
        setCountdown(seconds);
        if (countdownRef.current) clearInterval(countdownRef.current);

        countdownRef.current = setInterval(() => {
            setCountdown((prev) => {
                if (prev === null || prev <= 1) {
                    if (countdownRef.current) clearInterval(countdownRef.current);
                    addLog(`Инфо: Ровер ${roverName} успешно прибыл в точку назначения! Награда начислена.`);
                    onMissionComplete();
                    return null;
                }
                return prev - 1;
            });
        }, 1000);
    };

    // Находим сегмент маршрута между текущей позицией ровера и целью
    const selectedRouteSegment = activeRover && targetLocationId ? routes.find(
        (r) =>
            (r.from_location_id === activeRover.current_location_id && r.to_location_id === targetLocationId) ||
            (r.to_location_id === activeRover.current_location_id && r.from_location_id === targetLocationId)
    ) : null;

    const routeDistance = selectedRouteSegment ? selectedRouteSegment.distance_km : 0;
    const routeHazard = selectedRouteSegment ? (selectedRouteSegment.hazard_risk ?? 0) : 0;
    const estimatedTravelTime = routeDistance > 0 ? Math.max(5, Math.round(routeDistance * 1.5 * (1 + routeHazard / 50))) : 0;
    const estimatedEnergy = routeDistance > 0 && activeRover ? Math.round((routeDistance * 0.1) * (1 + cargoWeight / activeRover.max_payload) * (1 + routeHazard / 100)) : 0;
    const estimatedCredits = routeDistance > 0 ? Math.round(100 + routeDistance * 3 + cargoWeight * 1.5) : 0;
    const estimatedRep = routeDistance > 0 ? Math.round(5 + cargoWeight * 0.02 + routeDistance * 0.01) : 0;
    const repairCost = activeRover ? activeRover.wear * 10 : 0;

    const isDispatchDisabled =
        loading ||
        isGameOver ||
        !activeRover ||
        !targetLocationId ||
        activeRover.status !== 'idle' ||
        activeRover.now_battery_capacity <= 0 ||
        activeRover.wear >= 100 ||
        cargoWeight > activeRover.max_payload ||
        cargoWeight < 0;

    const handleDispatch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!activeRover || !targetLocationId) return;

        setError('');
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/rovers/dispatch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rover_id: activeRover.id,
                    target_location_id: targetLocationId,
                    cargo_mass: Number(cargoWeight),
                }),
            });

            const data: DispatchResponse & { detail?: string } = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || 'Ошибка отправки');
            }

            addLog(
                `Успешно: Ровер ${activeRover.name} отправлен в рейс! ` +
                `Энергия: -${data.energy_spent}%, Износ: +${data.wear_inflicted}%. ` +
                `Награда: +${data.reward_credits} CR, +${data.reward_rep} Rep. Время: ${data.travel_time_seconds} с.`
            );
            startCountdown(data.travel_time_seconds, activeRover.name);
            setTargetLocationId('');
            onMissionComplete();
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
            setError(errorMessage);
            addLog(`Ошибка: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const handleRepair = async () => {
        if (!activeRover) return;
        setError('');
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/rovers/${activeRover.id}/repair`, {
                method: 'POST',
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || 'Ошибка при ремонте');
            }
            addLog(`Ремонт завершён: Ровер ${activeRover.name} отремонтирован за ${data.cost_credits} CR.`);
            onMissionComplete();
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
            setError(errorMessage);
            addLog(`Ошибка ремонта: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const handleBuyRover = async (model: string) => {
        setError('');
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/rovers/buy`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model }),
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || 'Ошибка при покупке ровера');
            }
            addLog(`Покупка: Приобретён новый ровер "${data.name}" (${data.model})!`);
            setIsShopOpen(false);
            onMissionComplete();
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
            alert(`Ошибка покупки: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const handleCharge = async () => {
        if (!activeRover) return;
        setError('');
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/rovers/${activeRover.id}/charge`, {
                method: 'POST',
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || 'Ошибка при зарядке ровера');
            }

            addLog(`Успешно: Ровер ${activeRover.name} полностью заряжен (100%).`);
            onMissionComplete();
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
            setError(errorMessage);
            addLog(`Ошибка зарядки: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const getLocationName = (id: string | undefined) => {
        if (!id) return '—';
        return nodes.find((n) => n.id === id)?.name || id;
    };

    return (
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', margin: 0 }}>
                    Панель управления флотом
                </h2>
                <button
                    onClick={() => setIsShopOpen(!isShopOpen)}
                    style={{
                        padding: '6px 12px',
                        backgroundColor: '#10b981',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '4px',
                        fontWeight: 600,
                        cursor: 'pointer',
                        fontSize: '13px',
                    }}
                >
                    🛒 Магазин роверов
                </button>
            </div>

            {/* Shop Modal / Drawer */}
            {isShopOpen && (
                <div
                    style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid #3b82f6',
                        borderRadius: '6px',
                        padding: '12px',
                        marginBottom: '16px',
                    }}
                >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <div style={{ fontWeight: 700, color: '#38bdf8', fontSize: '14px' }}>
                            Доступные модели для покупки (Баланс: {stationBalance} CR)
                        </div>
                        <button
                            onClick={() => setIsShopOpen(false)}
                            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '16px' }}
                        >
                            ✕
                        </button>
                    </div>

                    {shopLoading ? (
                        <div style={{ color: '#94a3b8', fontSize: '13px' }}>Загрузка каталога...</div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                            {catalog.map((item) => (
                                <div
                                    key={item.model}
                                    style={{
                                        backgroundColor: '#1e293b',
                                        border: '1px solid #334155',
                                        padding: '10px',
                                        borderRadius: '4px',
                                        fontSize: '12px',
                                    }}
                                >
                                    <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '13px' }}>{item.model}</div>
                                    <div style={{ color: '#94a3b8', margin: '2px 0' }}>{item.description}</div>
                                    <div style={{ color: '#cbd5e1' }}>Грузоподъёмность: {item.max_payload} кг | Броня: {item.armor}</div>
                                    <div style={{ color: '#cbd5e1' }}>Батарея: {item.battery_capacity}% | Расход: {item.base_drain_rate}</div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px' }}>
                                        <span style={{ color: '#4ade80', fontWeight: 700 }}>💰 {item.price} CR</span>
                                        <button
                                            onClick={() => handleBuyRover(item.model)}
                                            disabled={loading || stationBalance < item.price}
                                            style={{
                                                padding: '4px 8px',
                                                backgroundColor: stationBalance >= item.price ? '#16a34a' : '#475569',
                                                color: '#ffffff',
                                                border: 'none',
                                                borderRadius: '4px',
                                                cursor: stationBalance >= item.price ? 'pointer' : 'not-allowed',
                                                fontSize: '11px',
                                                fontWeight: 600,
                                            }}
                                        >
                                            Купить
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Select Rover Buttons */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
                {rovers.map((r) => {
                    const isDamaged = r.wear >= 100 || r.status === 'damaged';
                    return (
                        <button
                            key={r.id}
                            onClick={() => {
                                setSelectedRoverId(r.id);
                                setTargetLocationId('');
                            }}
                            style={{
                                padding: '8px 12px',
                                backgroundColor: activeRover?.id === r.id ? '#3b82f6' : isDamaged ? '#991b1b' : '#334155',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '13px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                            }}
                        >
                            <span>{r.name}</span>
                            {isDamaged && <span title="Повреждён (Износ 100%)">⚠️</span>}
                        </button>
                    );
                })}
            </div>

            {activeRover ? (
                <form onSubmit={handleDispatch} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ backgroundColor: '#0f172a', padding: '12px', borderRadius: '4px', fontSize: '14px', color: '#e2e8f0' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span>Модель: <strong>{activeRover.model}</strong></span>
                            <span>Статус: <strong style={{ color: activeRover.status === 'idle' ? '#4ade80' : activeRover.status === 'en_route' ? '#fde047' : '#ef4444' }}>{activeRover.status}</strong></span>
                        </div>
                        <div>Заряд аккумулятора: <strong>{activeRover.now_battery_capacity}%</strong></div>
                        <div>Максимальный груз: <strong>{activeRover.max_payload} кг</strong></div>
                        <div>Броня: <strong>{activeRover.armor}</strong> (снижает урон в опасных зонах)</div>
                        <div style={{ marginTop: '2px' }}>
                            Износ ровера: <strong style={{ color: activeRover.wear > 70 ? '#ef4444' : activeRover.wear > 30 ? '#fde047' : '#4ade80' }}>{activeRover.wear}%</strong>
                        </div>
                        <div>Текущая локация: <strong>{getLocationName(activeRover.current_location_id)}</strong></div>

                        <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                            <button
                                type="button"
                                onClick={handleCharge}
                                disabled={loading || activeRover.now_battery_capacity >= 100 || activeRover.status !== 'idle'}
                                style={{
                                    padding: '6px 12px',
                                    backgroundColor: (activeRover.now_battery_capacity >= 100 || activeRover.status !== 'idle') ? '#475569' : '#0284c7',
                                    color: '#ffffff',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '12px',
                                    fontWeight: 600,
                                    cursor: (activeRover.now_battery_capacity >= 100 || activeRover.status !== 'idle') ? 'not-allowed' : 'pointer',
                                }}
                            >
                                ⚡ Зарядить до 100%
                            </button>

                            {activeRover.wear > 0 && (
                                <button
                                    type="button"
                                    onClick={handleRepair}
                                    disabled={loading || stationBalance < repairCost || activeRover.status === 'en_route'}
                                    style={{
                                        padding: '6px 12px',
                                        backgroundColor: stationBalance >= repairCost && activeRover.status !== 'en_route' ? '#d97706' : '#475569',
                                        color: '#ffffff',
                                        border: 'none',
                                        borderRadius: '4px',
                                        fontSize: '12px',
                                        fontWeight: 600,
                                        cursor: stationBalance >= repairCost && activeRover.status !== 'en_route' ? 'pointer' : 'not-allowed',
                                    }}
                                >
                                    🔧 Ремонт ({repairCost} CR)
                                </button>
                            )}
                        </div>
                    </div>

                    {countdown !== null && (
                        <div style={{
                            backgroundColor: '#422006',
                            border: '1px solid #ca8a04',
                            borderRadius: '4px',
                            padding: '10px',
                            fontSize: '14px',
                            color: '#fde047',
                            textAlign: 'center',
                        }}>
                            Прибытие через: {countdown} сек ⌛
                        </div>
                    )}

                    <label style={{ fontSize: '14px', color: '#e2e8f0' }}>
                        Точка назначения:
                        <select
                            value={targetLocationId}
                            onChange={(e) => setTargetLocationId(e.target.value)}
                            style={{
                                width: '100%',
                                boxSizing: 'border-box',
                                padding: '8px',
                                backgroundColor: '#0f172a',
                                color: '#ffffff',
                                border: '1px solid #475569',
                                borderRadius: '4px',
                                marginTop: '4px',
                            }}
                            required
                        >
                            <option value="">Выберите локацию</option>
                            {nodes
                                .filter((n) => n.id !== activeRover.current_location_id)
                                .map((n) => (
                                    <option key={n.id} value={n.id}>
                                        {n.name}
                                    </option>
                                ))}
                        </select>
                    </label>

                    {/* Выбор ровера перед отправкой непосредственно в форме */}
                    <label style={{ fontSize: '14px', color: '#e2e8f0' }}>
                        Выбор ровера для отправки:
                        <select
                            value={selectedRoverId}
                            onChange={(e) => {
                                setSelectedRoverId(e.target.value);
                                setTargetLocationId('');
                            }}
                            style={{
                                width: '100%',
                                boxSizing: 'border-box',
                                padding: '8px',
                                backgroundColor: '#0f172a',
                                color: '#ffffff',
                                border: '1px solid #475569',
                                borderRadius: '4px',
                                marginTop: '4px',
                            }}
                            required
                        >
                            {rovers.map((r) => {
                                const isDamaged = r.wear >= 100 || r.status === 'damaged';
                                const labelText = `${r.name} (${r.model}) - Заряд: ${r.now_battery_capacity}% - Износ: ${r.wear}% ${isDamaged ? '⚠️ ПОВРЕЖДЁН' : ''} [${r.status}]`;
                                return (
                                    <option key={r.id} value={r.id}>
                                        {labelText}
                                    </option>
                                );
                            })}
                        </select>
                    </label>

                    {/* Mission Forecast & Hazard Info */}
                    {targetLocationId && (
                        <div style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '10px', fontSize: '13px' }}>
                            <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: '4px' }}>Прогноз маршрута и зоны:</div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', color: '#cbd5e1' }}>
                                <div>Расстояние: <strong>{routeDistance > 0 ? `${routeDistance} км` : '—'}</strong></div>
                                <div>
                                    Опасность зоны: <strong style={{ color: routeHazard > 30 ? '#ef4444' : routeHazard > 10 ? '#fde047' : '#4ade80' }}>
                                        {routeHazard}% {routeHazard > 30 ? '⚠️ (Высокая)' : ''}
                                    </strong>
                                </div>
                                <div>Время в пути: <strong>~{estimatedTravelTime} сек</strong></div>
                                <div>Расход энергии: <strong>~{estimatedEnergy}%</strong></div>
                                <div>Награда (Деньги): <strong style={{ color: '#4ade80' }}>+{estimatedCredits} CR</strong></div>
                                <div>Награда (Репутация): <strong style={{ color: '#38bdf8' }}>+{estimatedRep} Rep</strong></div>
                            </div>
                        </div>
                    )}

                    <label style={{ fontSize: '14px', color: '#e2e8f0' }}>
                        Масса груза (кг):
                        <input
                            type="number"
                            min="0"
                            max={activeRover.max_payload}
                            value={cargoWeight}
                            onChange={(e) => setCargoWeight(Number(e.target.value))}
                            style={{
                                width: '100%',
                                boxSizing: 'border-box',
                                padding: '8px',
                                backgroundColor: '#0f172a',
                                color: '#ffffff',
                                border: '1px solid #475569',
                                borderRadius: '4px',
                                marginTop: '4px',
                            }}
                        />
                    </label>

                    {cargoWeight > activeRover.max_payload && (
                        <div style={{ color: '#f87171', fontSize: '13px' }}>
                            Превышена грузоподъёмность ({activeRover.max_payload} кг)
                        </div>
                    )}

                    {error && (
                        <div style={{
                            backgroundColor: '#451a1a',
                            border: '1px solid #991b1b',
                            borderRadius: '4px',
                            padding: '8px 12px',
                            color: '#fca5a5',
                            fontSize: '13px'
                        }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={isDispatchDisabled}
                        style={{
                            padding: '10px',
                            backgroundColor: isDispatchDisabled ? '#475569' : '#16a34a',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '4px',
                            fontWeight: 600,
                            cursor: isDispatchDisabled ? 'not-allowed' : 'pointer',
                            marginTop: '8px',
                        }}
                    >
                        {loading ? 'Обработка...' : 'Отправить ровер в рейс'}
                    </button>
                </form>
            ) : (
                <div style={{ color: '#94a3b8' }}>Нет доступных роверов</div>
            )}

            <div style={{ marginTop: '20px' }}>
                <h3 style={{ fontSize: '14px', marginBottom: '8px', color: '#94a3b8' }}>Логи событий и доставок</h3>
                <div
                    style={{
                        backgroundColor: '#020617',
                        padding: '10px',
                        borderRadius: '4px',
                        height: '110px',
                        overflowY: 'auto',
                        fontSize: '12px',
                        color: '#cbd5e1',
                        boxSizing: 'border-box',
                    }}
                >
                    {logs.length === 0 ? (
                        <div style={{ color: '#64748b' }}>Логи отсутствуют</div>
                    ) : (
                        logs.map((log, index) => <div key={index} style={{ marginBottom: '4px' }}>{log}</div>)
                    )}
                </div>
            </div>
        </div>
    );
};
