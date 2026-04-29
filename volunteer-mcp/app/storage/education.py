#!/usr/bin/env python3
import os
import json
import unicodedata
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def _build_engine_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return "sqlite:///data/education_jobs.db"


engine = create_engine(_build_engine_url(), echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class University(Base):
    __tablename__ = "universities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(256), index=True)
    siglas: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    rvoe: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    campuses: Mapped[List["Campus"]] = relationship("Campus", back_populates="university", cascade="all, delete-orphan")


class Campus(Base):
    __tablename__ = "campuses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))
    campus: Mapped[str] = mapped_column(String(256))
    ciudad: Mapped[str] = mapped_column(String(128))
    estado: Mapped[str] = mapped_column(String(128))
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    university: Mapped[University] = relationship("University", back_populates="campuses")


class JobPosting(Base):
    __tablename__ = "job_postings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), index=True)
    organization: Mapped[Optional[str]] = mapped_column(String(256))
    location: Mapped[Optional[str]] = mapped_column(String(256))
    area: Mapped[Optional[str]] = mapped_column(String(128))
    career: Mapped[Optional[str]] = mapped_column(String(128))
    link: Mapped[str] = mapped_column(String(512), unique=True)
    source: Mapped[Optional[str]] = mapped_column(String(256))
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(engine)


def save_jobs(items: List[Dict[str, Any]]) -> int:
    if not items:
        return 0
    init_db()
    saved = 0
    with SessionLocal() as session:
        for it in items:
            link = str(it.get("link") or it.get("url") or "")
            if not link:
                continue
            posted_at = None
            pts = it.get("posted_at")
            if isinstance(pts, str):
                try:
                    posted_at = datetime.fromisoformat(pts)
                except Exception:
                    posted_at = None
            job = JobPosting(
                title=(it.get("title") or it.get("position") or "").strip(),
                organization=(it.get("organization") or it.get("org") or None),
                location=it.get("location") or None,
                area=((it.get("area") or "")[:128] or None) if it.get("area") else None,
                career=(it.get("career") if isinstance(it.get("career"), str) else ",".join(it.get("career", []))) or None,
                link=link,
                source=it.get("source") or None,
                posted_at=posted_at,
            )
            try:
                session.add(job)
                session.commit()
                saved += 1
            except IntegrityError:
                session.rollback()
                continue
    return saved


def _job_to_dict(j: JobPosting) -> Dict[str, Any]:
    return {
        "id": j.id,
        "title": j.title,
        "organization": j.organization,
        "location": j.location,
        "area": j.area,
        "career": j.career,
        "link": j.link,
        "source": j.source,
        "posted_at": j.posted_at.isoformat() if j.posted_at else None,
        "created_at": j.created_at.isoformat() if j.created_at else None,
    }


def list_jobs(
    q: Optional[str] = None,
    location: Optional[str] = None,
    area: Optional[str] = None,
    career: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> Dict[str, Any]:
    init_db()
    with SessionLocal() as session:
        query = session.query(JobPosting)
        if q:
            like = f"%{q}%"
            query = query.filter(JobPosting.title.ilike(like))
        if location:
            like = f"%{location}%"
            query = query.filter(JobPosting.location.ilike(like))
        if area:
            like = f"%{area}%"
            query = query.filter(JobPosting.area.ilike(like))
        if career:
            like = f"%{career}%"
            query = query.filter(JobPosting.career.ilike(like))
        total = query.count()
        items = query.order_by(JobPosting.created_at.desc()).offset(offset).limit(limit).all()
        return {"total": total, "items": [_job_to_dict(i) for i in items]}


# --- Lectura de blobs educativos (Redis o archivos) ---

def get_edu_enriched(redis_client: Any = None, data_dir: str = "data") -> Dict[str, Any]:
    if redis_client is not None:
        try:
            raw = redis_client.get("edu:enriched")
            if raw:
                data = json.loads(raw)
                count = len(data) if isinstance(data, list) else 1
                return {"success": True, "count": count, "data": data}
        except Exception:
            pass
    path = os.path.join(data_dir, "edu_enriched.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = len(data) if isinstance(data, list) else 1
        return {"success": True, "count": count, "data": data}
    return {"success": True, "count": 0, "data": []}


def get_edu_details(redis_client: Any = None, data_dir: str = "data") -> Dict[str, Any]:
    if redis_client is not None:
        try:
            raw = redis_client.get("edu:details")
            if raw:
                data = json.loads(raw)
                count = len(data) if isinstance(data, list) else 1
                return {"success": True, "count": count, "data": data}
        except Exception:
            pass
    path = os.path.join(data_dir, "edu_details.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = len(data) if isinstance(data, list) else 1
        return {"success": True, "count": count, "data": data}
    return {"success": True, "count": 0, "data": []}


def _normalize_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text or "")
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = " ".join(text.split())
    return text


def get_edu_all_combined(redis_client: Any = None, data_dir: str = "data") -> Dict[str, Any]:
    def _key(name: str, state: str = "") -> str:
        return f"{_normalize_text(name)}|{_normalize_text(state)}"

    resp_e = get_edu_enriched(redis_client, data_dir)
    resp_d = get_edu_details(redis_client, data_dir)
    enriched_data = resp_e.get("data") if isinstance(resp_e.get("data"), list) else []
    details_data = resp_d.get("data") if isinstance(resp_d.get("data"), list) else []

    details_index: Dict[str, Any] = {}
    for d in details_data or []:
        nombre = d.get("nombre") or d.get("name") or ""
        details_index[_key(nombre, "")] = d

    combined = []
    for e in enriched_data or []:
        state = e.get("state") or ""
        name = e.get("name") or e.get("nombre") or ""
        d = details_index.get(_key(name, state)) or details_index.get(_key(name, ""))
        merged = dict(e)
        if d:
            if "carreras" in d:
                merged["carreras"] = d.get("carreras")
            if "costo" in d:
                merged["costo"] = d.get("costo")
            if d.get("ubicacion"):
                merged["ubicacion"] = d.get("ubicacion")
            merged["details_raw"] = d
        combined.append(merged)
    return {"success": True, "count": len(combined), "data": combined}
