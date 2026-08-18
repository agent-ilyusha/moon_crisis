import uuid

<<<<<<< HEAD
from sqlalchemy import CHAR, UUID, TypeDecorator, event, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as string without dashes.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value).hex
            else:
                return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


class Base(DeclarativeBase):
    pass


class UUIDMixin(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )


@event.listens_for(Base, "before_update", propagate=True)
def validate_immutable_id(mapper, connection, target):
    if isinstance(target, UUIDMixin):
        state = inspect(target)
        id_check = state.get_history("id", True)
        if id_check.has_changes():
            raise ValueError("Поле id нельзя обновлять!")
=======
from pydantic import ValidationError
from sqlalchemy import Column, event, inspect, UUID
from sqlalchemy.orm import declarative_base, Mapped

Base = declarative_base()


class UUID_Mixin(Base):
    """
    Id for models.
    """
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    class Meta:
        abstract = True
        unique_together = (("id",),)


@event.listens_for(UUID_Mixin, 'before_update')
def validate_immutable_id(mapper, connection, target: UUID_Mixin):
    state = inspect(target)
    id_check = state.get_history('id', True)
    if id_check.has_changes():
        raise ValidationError("Поле id нельзя обновлять!")


>>>>>>> 1ad351b05d98169fa8961cb9e6d17a2a16741fa2
