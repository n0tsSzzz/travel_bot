from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.meta import Base, metadata

from sqlalchemy import BigInteger



class User(Base):
    __tablename__ = "users"

    user_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, nullable=False, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)

    trips: Mapped[list["Trip"]] = relationship(back_populates="user", cascade='all, delete')
    items: Mapped[list["Item"]] = relationship(back_populates="user", cascade='all, delete')
