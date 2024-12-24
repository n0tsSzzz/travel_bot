from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.meta import Base, metadata

# from .trip import Trip
# from .item import Item
from sqlalchemy import BigInteger



class User(Base):
    __tablename__ = "users"

    user_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, nullable=False, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)

    trips = relationship("Trip", back_populates="user", cascade='all, delete')
    items = relationship("Item", back_populates="user", cascade='all, delete')
