from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.meta import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), )
    days_needed: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[BigInteger] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    user = relationship("User", back_populates="trips")

    items = relationship("Item", back_populates="trip")