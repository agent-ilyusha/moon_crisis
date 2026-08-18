import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from app.database import engine

from app.models.general import Base

from app.models.Factions import Faction, Factions_relationship, Station_faction_reputation
from app.models.Map import Map, LocationType
from app.models.Route import RouteSegment
from app.models.Rover import Rover
from app.models.Station import Station
from app.models.User import User


def seed_database():
    print("Таблицы, готовые к созданию:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)

    db: Session = Session(bind=engine)

    try:
        print("Запуск сидирования Лунной логистической сети...")
        with Session(bind=engine) as db:
            if db.query(Faction).first():
                print("База данных уже содержит начальные данные. Пропуск сидирования.")
                return

            factions = [
                Faction(
                    id=uuid.uuid4(),
                    name="Lunar Mining Syndicate",
                    tag="LMS",
                    description="Mining and extraction conglomerate."
                ),
                Faction(
                    id=uuid.uuid4(),
                    name="Artemis Science Alliance",
                    tag="ASA",
                    description="Scientific research and technological advancement."
                ),
                Faction(
                    id=uuid.uuid4(),
                    name="Helium-3 Corporation",
                    tag="H3C",
                    description="Energy production and fuel supply monopoly."
                ),
            ]
            db.add_all(factions)
            db.flush()

            alpha = Map(
                id=uuid.uuid4(),
                name="Alpha Outpost",
                coord_x=0.0,
                coord_y=0.0,
                location_type=LocationType.base,
                controlling_faction_id=factions[0].id,
                has_charging=True
            )
            shackleton = Map(
                id=uuid.uuid4(),
                name="Shackleton Crater",
                coord_x=12.5,
                coord_y=45.2,
                location_type=LocationType.mine,
                controlling_faction_id=factions[0].id,
                has_charging=False
            )
            tranquillity = Map(
                id=uuid.uuid4(),
                name="Mare Tranquillitatis",
                coord_x=-30.0,
                coord_y=15.8,
                location_type=LocationType.science_lab,
                controlling_faction_id=factions[1].id,
                has_charging=True
            )
            tycho = Map(
                id=uuid.uuid4(),
                name="Tycho Base",
                coord_x=50.1,
                coord_y=-10.4,
                location_type=LocationType.outpost,
                controlling_faction_id=factions[2].id,
                has_charging=True
            )

            maps = [alpha, shackleton, tranquillity, tycho]
            db.add_all(maps)
            db.flush()

            relationships = [
                Factions_relationship(
                    id=uuid.uuid4(),
                    first_faction_id=factions[0].id,
                    second_faction_id=factions[1].id,
                    reputation_impact=-3.0,
                ),
                Factions_relationship(
                    id=uuid.uuid4(),
                    first_faction_id=factions[0].id,
                    second_faction_id=factions[2].id,
                    reputation_impact=-2.0,
                ),
                Factions_relationship(
                    id=uuid.uuid4(),
                    first_faction_id=factions[1].id,
                    second_faction_id=factions[2].id,
                    reputation_impact=-4.0,
                ),
            ]
            db.add_all(relationships)
            db.flush()

            routes = [
                RouteSegment(
                    id=uuid.uuid4(),
                    from_location_id=alpha.id,
                    to_location_id=shackleton.id,
                    distance_km=150.0,
                    hazard_risk=15,
                    base_energy_cost=20,
                ),
                RouteSegment(
                    id=uuid.uuid4(),
                    from_location_id=shackleton.id,
                    to_location_id=tranquillity.id,
                    distance_km=320.0,
                    hazard_risk=45,
                    base_energy_cost=45,
                ),
                RouteSegment(
                    id=uuid.uuid4(),
                    from_location_id=alpha.id,
                    to_location_id=tranquillity.id,
                    distance_km=210.0,
                    hazard_risk=10,
                    base_energy_cost=30,
                ),
                RouteSegment(
                    id=uuid.uuid4(),
                    from_location_id=tranquillity.id,
                    to_location_id=tycho.id,
                    distance_km=500.0,
                    hazard_risk=60,
                    base_energy_cost=70,
                ),
            ]
            db.add_all(routes)
            db.flush()

            test_user = User(
                id=uuid.uuid4(),
                username="commander_one",
                hashed_password="some_secure_hashed_password_string",
                role="commander",
                created_at=datetime.utcnow(),
            )
            db.add(test_user)
            db.flush()

            home_station = Station(
                id=uuid.uuid4(),
                name="Alpha Outpost Command",
                balance=5000,
                reputation=150,
                fleet_capacity=10,
                location_id=alpha.id,
                user_id=test_user.id,
                faction_id=factions[0].id,
            )
            db.add(home_station)
            db.flush()

            # Начальная репутация с каждой фракцией (по 50 очков)
            for f in factions:
                db.add(
                    Station_faction_reputation(
                        id=uuid.uuid4(),
                        station_id=home_station.id,
                        faction_id=f.id,
                        reputation=50,
                    )
                )
            db.flush()

            starter_rover = Rover(
                id=uuid.uuid4(),
                name="Scout-01",
                model="Mule-Mk1",
                max_payload=500,
                battery_capacity=100,
                base_drain_rate=5,
                armor=50,
                now_battery_capacity=100,
                position_x=alpha.coord_x,
                position_y=alpha.coord_y,
                status="idle",
                wear=0,
                current_location_id=alpha.id,
                station_id=home_station.id,
            )
            db.add(starter_rover)

            db.commit()
            print("Сидирование успешно завершено! Создана карта, фракции, стартовая станция и ровер Scout-01.")
    except Exception as e:
        db.rollback()
        print(f"Ошибка сидирования базы данных: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
