from sqlalchemy import Column, Integer, String, Float as SQLFloat, DateTime, ForeignKey, JSON, Index, BigInteger
from sqlalchemy.orm import relationship
from .db import Base

class Float(Base):
    __tablename__ = "floats"
    float_id = Column(Integer, primary_key=True, index=True)
    platform_number = Column(BigInteger, unique=True, index=True)
    launch_date = Column(DateTime, nullable=True)
    last_contact = Column(DateTime, nullable=True)
    platform_type = Column(String(128), nullable=True)
    region = Column(String(128), index=True)

    profiles = relationship("Profile", back_populates="float")

class Profile(Base):
    __tablename__ = "profiles"
    profile_id = Column(Integer, primary_key=True, index=True)
    float_id = Column(Integer, ForeignKey("floats.float_id"), index=True)
    platform_number = Column(BigInteger, index=True)
    cycle_number = Column(Integer, index=True)
    profile_index = Column(Integer)
    datetime = Column(DateTime, index=True)
    julian_day = Column(SQLFloat)
    latitude = Column(SQLFloat, index=True)
    longitude = Column(SQLFloat, index=True)
    pressure = Column(SQLFloat)
    temperature = Column(SQLFloat)
    salinity = Column(SQLFloat)
    depth = Column(SQLFloat)
    pres_error = Column(SQLFloat)
    temp_error = Column(SQLFloat)
    sal_error = Column(SQLFloat)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    salinity_bin = Column(String(16))
    source_file = Column(String(512))

    float = relationship("Float", back_populates="profiles")
    summary = relationship("ProfileSummary", back_populates="profile", uselist=False)

Index("idx_profiles_lat_lon_time", Profile.latitude, Profile.longitude, Profile.datetime)

class ProfileSummary(Base):
    __tablename__ = "profile_summary"
    profile_id = Column(Integer, ForeignKey("profiles.profile_id"), primary_key=True)
    summary_text = Column(String(2048))
    # store embedding as list in JSON for portability (Chroma stores vectors separately)
    embedding = Column(JSON)

    profile = relationship("Profile", back_populates="summary")
