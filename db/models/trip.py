from sqlalchemy import Text, Integer, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from datetime import datetime

from db.models.meta import Base, metadata


class Trip(Base):
    __tablename__ = 'trips'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), )
    days_needed: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[BigInteger] = mapped_column(ForeignKey("users.user_id", ondelete='CASCADE'))
    user: Mapped["User"] = relationship(back_populates="trips")

    items: Mapped["Item"] = relationship(back_populates="trip")