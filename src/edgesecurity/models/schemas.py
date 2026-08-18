from pydantic import BaseModel


class TokenCreateRequest(BaseModel):
    node_id: str
    hardware_secret: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class VerifyTokenRequest(BaseModel):
    token: str

class VerifyTokenResponse(BaseModel):
    is_valid: bool
    node_id: str | None = None
    role: str | None = None

class APIKeyCreateRequest(BaseModel):
    service_name: str
    role: str

class APIKeyResponse(BaseModel):
    service_name: str
    api_key: str
    role: str
