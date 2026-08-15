from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    positive_reviews: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    negative_reviews: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_turnover: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    turnover_30_days: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    # Будущее:
    # депозит пользователя
    deposit: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    guarantor = relationship(
        "Guarantor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    reviews_received = relationship(
        "Review",
        foreign_keys="Review.target_user_id",
        back_populates="target_user",
        cascade="all, delete-orphan",
    )

    reviews_given = relationship(
        "Review",
        foreign_keys="Review.author_user_id",
        back_populates="author_user",
        cascade="all, delete-orphan",
    )


# ============================================================
# ORDER
# ============================================================

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # buy = пользователь хочет купить крипту
    # sell = пользователь хочет продать крипту
    order_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    fiat: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    coin: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    amount: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Курс фиксируется в момент создания ордера.
    rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    conditions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    user = relationship(
        "User",
        back_populates="orders",
    )

    trades_as_order = relationship(
        "Trade",
        foreign_keys="Trade.order_id",
        back_populates="order",
    )


# ============================================================
# TRADE
# ============================================================

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    guarantor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="waiting_guarantor",
        nullable=False,
        index=True,
    )

    # Сумма сделки
    amount: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    fiat: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    coin: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Курс фиксируется для конкретной сделки.
    rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    seller = relationship(
        "User",
        foreign_keys=[seller_id],
    )

    buyer = relationship(
        "User",
        foreign_keys=[buyer_id],
    )

    guarantor = relationship(
        "User",
        foreign_keys=[guarantor_id],
    )

    order = relationship(
        "Order",
        foreign_keys=[order_id],
        back_populates="trades_as_order",
    )

    events = relationship(
        "TradeEvent",
        back_populates="trade",
        cascade="all, delete-orphan",
    )

    reviews = relationship(
        "Review",
        back_populates="trade",
        cascade="all, delete-orphan",
    )


# ============================================================
# GUARANTOR
# ============================================================

class Guarantor(Base):
    __tablename__ = "guarantors"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="guarantor",
    )


# ============================================================
# REVIEW
# ============================================================

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    trade_id: Mapped[int] = mapped_column(
        ForeignKey("trades.id"),
        nullable=False,
    )

    author_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # positive / negative
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    trade = relationship(
        "Trade",
        back_populates="reviews",
    )

    author_user = relationship(
        "User",
        foreign_keys=[author_user_id],
        back_populates="reviews_given",
    )

    target_user = relationship(
        "User",
        foreign_keys=[target_user_id],
        back_populates="reviews_received",
    )


# ============================================================
# TRADE EVENT
# ============================================================

class TradeEvent(Base):
    __tablename__ = "trade_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    trade_id: Mapped[int] = mapped_column(
        ForeignKey("trades.id"),
        nullable=False,
        index=True,
    )

    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    trade = relationship(
        "Trade",
        back_populates="events",
    )
