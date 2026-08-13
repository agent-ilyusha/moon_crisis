import uuid

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


