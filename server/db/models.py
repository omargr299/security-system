
from typing import List, Set
from sqlalchemy import ForeignKey, Integer, String, Table, Column, true
import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import uuid


class Base(DeclarativeBase):
    pass


vehicles_users = Table(
    "vehicles_users",
    Base.metadata,
    Column("userId", UUID, ForeignKey("users.id")),
    Column("vehicleId", UUID, ForeignKey("vehicles.id")),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(30))
    lastname: Mapped[str] = mapped_column(String(30))
    registerNumber: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=True)

    face: Mapped["Face"] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    qr: Mapped["QR"] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    vehicles: Mapped[Set["Vehicle"]] = relationship(
        secondary=vehicles_users, back_populates="users", cascade="save-update")

    def __repr__(self):
        return f"User(name={self.name}, lastname={self.lastname})"


class Face(Base):
    __tablename__ = "faces"
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    label: Mapped[int] = mapped_column(
        sqlalchemy.Sequence('label_seq', start=1, increment=1, data_type=Integer), unique=True)
    userId: Mapped[int] = mapped_column(UUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        back_populates="face")

    def __repr__(self):
        return f"Face(user={self.user} label={self.label})"


class QR(Base):
    __tablename__ = "qrs"
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    hashCode: Mapped[str] = mapped_column(String(30))
    userId: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        back_populates="qr")

    def __repr__(self):
        return f"QR(user={self.user.name} hash_code={self.hashCode})"


class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    plate: Mapped[str] = mapped_column(String(30), unique=True)
    brand: Mapped[str] = mapped_column(String(30), nullable=True)
    model: Mapped[str] = mapped_column(String(30), nullable=True)
    color: Mapped[str] = mapped_column(String(30), nullable=True)
    users: Mapped[Set["User"]] = relationship(
        secondary=vehicles_users, back_populates="vehicles")

    def __repr__(self) -> str:

        return f"Vehicle(plate={self.plate} model={self.model} brand={self.brand} color={self.color})"


class Employe(Base):
    __tablename__ = "employes"
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(30))
    lastname: Mapped[str] = mapped_column(String(30))
    registerNumber: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(15))

    def __repr__(self):
        return f"Employe(name={self.name}, lastname={self.lastname})"


if __name__ == "__main__":
    engine = sqlalchemy.create_engine(
        "postgresql+psycopg2://postgres:1234@localhost:5432/security-system", echo=True)
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
