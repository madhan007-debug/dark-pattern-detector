from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Connect to a local SQLite file called dev.db (created automatically)
engine = create_engine("sqlite:///dev.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True)
    domain = Column(String, nullable=False)
    last_scanned_at = Column(DateTime, default=datetime.utcnow)


class PatternType(Base):
    __tablename__ = "pattern_types"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)


class LegalClause(Base):
    __tablename__ = "legal_clauses"
    id = Column(Integer, primary_key=True)
    pattern_type_id = Column(Integer, ForeignKey("pattern_types.id"))
    law_name = Column(String, nullable=False)
    clause_text = Column(Text, nullable=False)
    pattern_type = relationship("PatternType")


class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    pattern_type_id = Column(Integer, ForeignKey("pattern_types.id"))
    confidence_score = Column(Float)
    detected_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    site = relationship("Site")
    pattern_type = relationship("PatternType")


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    detection_id = Column(Integer, ForeignKey("detections.id"))
    correct = Column(Boolean)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    detection = relationship("Detection")


def init_db():
    """Creates all tables in dev.db if they don't already exist"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()