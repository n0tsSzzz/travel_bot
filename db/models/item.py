from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.models.meta import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    user_id: Mapped[BigInteger] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    user = relationship("User", back_populates="items")

    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), nullable=True)
    trip = relationship("Trip", back_populates="items")
