"""
Authentication API routes
"""

import logging
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import Tenant, TenantUser, TenantStatus, UserRole, UserStatus
from src.auth.jwt import create_access_token
from src.auth.password import hash_password, verify_password
from src.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    """Signup request model"""
    tenant_name: str
    email: EmailStr
    password: str
    full_name: str


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict
    tenant: dict


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new tenant and owner user
    
    Creates:
    - New tenant with FREE plan
    - Owner user account
    - Returns JWT token
    """
    async for session in db:
        try:
            existing_user = await session.execute(
                select(TenantUser).where(TenantUser.email == request.email)
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            tenant_slug = request.tenant_name.lower().replace(" ", "-")
            
            existing_tenant = await session.execute(
                select(Tenant).where(Tenant.slug == tenant_slug)
            )
            if existing_tenant.scalar_one_or_none():
                tenant_slug = f"{tenant_slug}-{str(uuid.uuid4())[:8]}"
            
            tenant = Tenant(
                name=request.tenant_name,
                slug=tenant_slug,
                email=request.email,
                status=TenantStatus.ACTIVE
            )
            session.add(tenant)
            await session.flush()
            
            user = TenantUser(
                tenant_id=tenant.id,
                email=request.email,
                password_hash=hash_password(request.password),
                full_name=request.full_name,
                role=UserRole.OWNER,
                status=UserStatus.ACTIVE
            )
            session.add(user)
            
            await session.commit()
            await session.refresh(tenant)
            await session.refresh(user)
            
            token_data = {
                "user_id": str(user.id),
                "tenant_id": str(tenant.id),
                "email": user.email,
                "role": user.role.value
            }
            access_token = create_access_token(
                token_data,
                expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
            )
            
            logger.info(f"New tenant created: {tenant.name} ({tenant.id})")
            
            return AuthResponse(
                access_token=access_token,
                user={
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value
                },
                tenant={
                    "id": str(tenant.id),
                    "name": tenant.name,
                    "slug": tenant.slug,
                    "plan": tenant.plan.value,
                    "status": tenant.status.value
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Signup error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create account"
            )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password
    
    Returns JWT token
    """
    async for session in db:
        try:
            stmt = select(TenantUser).where(TenantUser.email == request.email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user or not verify_password(request.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            if user.status != UserStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is not active"
                )
            
            tenant_stmt = select(Tenant).where(Tenant.id == user.tenant_id)
            tenant_result = await session.execute(tenant_stmt)
            tenant = tenant_result.scalar_one()
            
            if tenant.status != TenantStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant account is not active"
                )
            
            token_data = {
                "user_id": str(user.id),
                "tenant_id": str(tenant.id),
                "email": user.email,
                "role": user.role.value
            }
            access_token = create_access_token(
                token_data,
                expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
            )
            
            user.last_login_at = datetime.utcnow()
            await session.commit()
            
            logger.info(f"User logged in: {user.email}")
            
            return AuthResponse(
                access_token=access_token,
                user={
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value
                },
                tenant={
                    "id": str(tenant.id),
                    "name": tenant.name,
                    "slug": tenant.slug,
                    "plan": tenant.plan.value,
                    "status": tenant.status.value
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
