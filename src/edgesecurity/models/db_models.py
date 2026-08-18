from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class EdgeNodeSecret(Base): # type: ignore[valid-type, misc]
    __tablename__ = "edge_node_secrets"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, unique=True, index=True, nullable=False)
    hashed_secret = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CloudServiceKey(Base): # type: ignore[valid-type, misc]
    __tablename__ = "cloud_service_keys"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True, index=True, nullable=False)
    hashed_api_key = Column(String, nullable=False)
    role = Column(String, default="read-only")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
