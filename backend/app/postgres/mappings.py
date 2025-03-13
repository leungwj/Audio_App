from typing import List, Optional
from sqlalchemy import ForeignKey, String, CHAR, Integer, Text, Float, ARRAY, Date, BINARY, Uuid, Boolean, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import uuid4, UUID
from datetime import date, datetime
import hashlib, os, secrets

class Base(DeclarativeBase):
    created_at: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deleted_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

# --------------------------------------------------------------------------------------------------------------------------------------

class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(60))
    full_name: Mapped[str] = mapped_column(String(50))
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # one-to-many relationship
    audio_files: Mapped[List["Audio_File"]] = relationship(back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'User (Email: {self.email!r}, Name: {self.full_name!r})'
    
    def authenticate(self, hashed_password: str):
        return secrets.compare_digest(hashed_password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
class Audio_File(Base):
    __tablename__ = 'audio_files'

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey(column='users.id', ondelete='CASCADE', onupdate='CASCADE'))
    description: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    audio_data: Mapped[str] = mapped_column(String(100))

    # many-to-one relationship
    user: Mapped["User"] = relationship(back_populates='audio_files')

    def __repr__(self):
        return f'Audio_File (Description: {self.description!r}, Category: {self.category!r})'