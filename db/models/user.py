from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.meta import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, nullable=False, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)

    trips = relationship("Trip", back_populates="user", cascade="all, delete")
    items = relationship("Item", back_populates="user", cascade="all, delete")
