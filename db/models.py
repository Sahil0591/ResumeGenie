from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, TIMESTAMP, JSON, Boolean, func
import uuid

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    source: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    company: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(Text, nullable=True)
    salary: Mapped[str] = mapped_column(Text, nullable=True)
    apply_url: Mapped[str] = mapped_column(Text, nullable=True)
    seniority: Mapped[str] = mapped_column(Text, nullable=True)
    remote_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    fetched_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    score: Mapped[int] = mapped_column(nullable=True)

class ApplicationPackage(Base):
    __tablename__ = "application_packages"
    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(Text)
    resume_markdown: Mapped[str] = mapped_column(Text)
    cheat_sheet_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
