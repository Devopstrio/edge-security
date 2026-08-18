import secrets
from datetime import timedelta

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from edgesecurity.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from edgesecurity.database import get_db
from edgesecurity.models.db_models import CloudServiceKey, EdgeNodeSecret
from edgesecurity.models.schemas import (
    APIKeyCreateRequest,
    APIKeyResponse,
    TokenCreateRequest,
    TokenResponse,
    VerifyTokenRequest,
    VerifyTokenResponse,
)

logger = structlog.get_logger()
router = APIRouter()

@router.post("/auth/token", response_model=TokenResponse)
async def issue_token(req: TokenCreateRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:  # noqa: B008
    # Validate against vault
    result = await db.execute(select(EdgeNodeSecret).where(EdgeNodeSecret.node_id == req.node_id))
    node = result.scalars().first()
    
    if not node or not verify_password(req.hardware_secret, node.hashed_secret):  # type: ignore[arg-type]
        logger.warning("Failed authentication attempt", node_id=req.node_id)
        raise HTTPException(status_code=401, detail="Invalid hardware secret or node ID")
        
    # Generate JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": req.node_id, "role": "edge_node"}, 
        expires_delta=access_token_expires
    )
    
    logger.info("Issued JWT token", node_id=req.node_id)
    return TokenResponse(access_token=access_token, token_type="bearer", expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

@router.post("/auth/verify", response_model=VerifyTokenResponse)
async def verify_token(req: VerifyTokenRequest) -> VerifyTokenResponse:
    decoded = decode_access_token(req.token)
    if not decoded:
        return VerifyTokenResponse(is_valid=False)
        
    return VerifyTokenResponse(
        is_valid=True,
        node_id=decoded.get("sub"),
        role=decoded.get("role")
    )

@router.post("/keys/generate", response_model=APIKeyResponse)
async def generate_api_key(req: APIKeyCreateRequest, db: AsyncSession = Depends(get_db)) -> APIKeyResponse:  # noqa: B008
    # In production, this route itself must be protected by an admin token.
    # We generate a secure random 32-byte API Key.
    raw_api_key = secrets.token_urlsafe(32)
    hashed_key = get_password_hash(raw_api_key)
    
    # Store the hash in DB
    new_key = CloudServiceKey(
        service_name=req.service_name,
        hashed_api_key=hashed_key,
        role=req.role
    )
    db.add(new_key)
    await db.commit()
    
    logger.info("Generated new API Key", service=req.service_name)
    # We only ever return the raw key once
    return APIKeyResponse(
        service_name=req.service_name,
        api_key=raw_api_key,
        role=req.role
    )

# Utility for tests to seed a node secret
@router.post("/_internal/seed-node", include_in_schema=False)
async def seed_node(node_id: str, raw_secret: str, db: AsyncSession = Depends(get_db)) -> dict[str, str]:  # noqa: B008
    new_node = EdgeNodeSecret(
        node_id=node_id,
        hashed_secret=get_password_hash(raw_secret)
    )
    db.add(new_node)
    await db.commit()
    return {"status": "seeded"}
