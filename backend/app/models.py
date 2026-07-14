from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ContactGroup(Base):
    __tablename__ = "contact_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    phone_numbers: Mapped[list["PhoneNumber"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    group_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("contact_groups.id"), nullable=True
    )
    sequence_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    group: Mapped[ContactGroup | None] = relationship(back_populates="phone_numbers")


class SoundboardClip(Base):
    __tablename__ = "soundboard_clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    voice_id: Mapped[str] = mapped_column(String, nullable=False)
    voice_name: Mapped[str | None] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class CallLog(Base):
    __tablename__ = "call_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("phone_numbers.id"), nullable=True
    )
    direction: Mapped[str] = mapped_column(String, default="outbound")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class BaitModule(Base):
    """A persona 'module': an ordered call script plus tiered filler clips.

    This is the data-driven replacement for the hardcoded persona in the
    legacy voice_search_baiter.py script.
    """

    __tablename__ = "bait_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    clips: Mapped[list["ModuleClip"]] = relationship(
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="ModuleClip.position",
    )


class ModuleClip(Base):
    __tablename__ = "module_clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bait_modules.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String, nullable=False)  # "script" | "filler"
    label: Mapped[str] = mapped_column(String, nullable=False)
    # URL path servable by an existing static mount, e.g.
    # "/soundboard-files/Walter Nelson/x.wav" or "/audio/modules/ab12.wav"
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    tier: Mapped[int | None] = mapped_column(Integer, nullable=True)  # fillers: 1-3
    expected_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    module: Mapped[BaitModule] = relationship(back_populates="clips")


class LegacyClip(Base):
    __tablename__ = "legacy_clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    display_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
