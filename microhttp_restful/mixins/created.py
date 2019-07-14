from datetime import datetime

from sqlalchemy import DateTime
from microhttp_restful import Field


class CreatedMixin:
    created_at = Field(
        DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
        readonly=True
    )
