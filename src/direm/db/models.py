from datetime import datetime, time

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from direm.domain.constants import DeliveryStatus, ReminderStatus
from direm.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    language_code: Mapped[str] = mapped_column(String(8), default="ru", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    reminders: Mapped[list["Reminder"]] = relationship(back_populates="user")
    deliveries: Mapped[list["ReminderDelivery"]] = relationship(back_populates="user")
    states: Mapped[list["UserState"]] = relationship(back_populates="user")


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(32), nullable=False)
    interval_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    daily_time: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    active_from: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    active_to: Mapped[time | None] = mapped_column(Time(timezone=False), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=ReminderStatus.ACTIVE.value,
        index=True,
        nullable=False,
    )
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

    user: Mapped[User] = relationship(back_populates="reminders")
    deliveries: Mapped[list["ReminderDelivery"]] = relationship(back_populates="reminder")


class ReminderDelivery(Base):
    __tablename__ = "reminder_deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    reminder_id: Mapped[int] = mapped_column(ForeignKey("reminders.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=DeliveryStatus.SKIPPED.value, index=True, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reminder: Mapped[Reminder] = relationship(back_populates="deliveries")
    user: Mapped[User] = relationship(back_populates="deliveries")


class UserState(Base):
    __tablename__ = "user_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="states")
