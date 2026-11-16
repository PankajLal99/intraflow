"""
Workflow API routes
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.database.models import WorkflowStatus
from src.services.workflow_service import WorkflowService
from src.auth.jwt import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])


class WorkflowCreate(BaseModel):
    """Workflow creation request"""
    name: str
    description: Optional[str] = None
    definition: Dict[str, Any]


class WorkflowUpdate(BaseModel):
    """Workflow update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Workflow response model"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    definition: Dict[str, Any]
    version: int
    status: str
    is_default: bool
    created_at: str
    updated_at: str


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    request: WorkflowCreate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new workflow for the authenticated tenant
    """
    async for session in db:
        try:
            workflow_service = WorkflowService()
            
            workflow = await workflow_service.create_workflow(
                session=session,
                tenant_id=UUID(current_user["tenant_id"]),
                name=request.name,
                description=request.description,
                definition=request.definition,
                created_by=UUID(current_user["user_id"])
            )
            
            return WorkflowResponse(
                id=str(workflow.id),
                tenant_id=str(workflow.tenant_id),
                name=workflow.name,
                description=workflow.description,
                definition=workflow.definition,
                version=workflow.version,
                status=workflow.status.value,
                is_default=workflow.is_default,
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create workflow"
            )


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List workflows for the authenticated tenant
    """
    async for session in db:
        try:
            workflow_service = WorkflowService()
            
            workflow_status = None
            if status_filter:
                try:
                    workflow_status = WorkflowStatus[status_filter.upper()]
                except KeyError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid status: {status_filter}"
                    )
            
            workflows = await workflow_service.list_workflows(
                session=session,
                tenant_id=UUID(current_user["tenant_id"]),
                status=workflow_status,
                limit=limit,
                offset=offset
            )
            
            return [
                WorkflowResponse(
                    id=str(w.id),
                    tenant_id=str(w.tenant_id),
                    name=w.name,
                    description=w.description,
                    definition=w.definition,
                    version=w.version,
                    status=w.status.value,
                    is_default=w.is_default,
                    created_at=w.created_at.isoformat(),
                    updated_at=w.updated_at.isoformat()
                )
                for w in workflows
            ]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list workflows"
            )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific workflow by ID
    """
    async for session in db:
        try:
            workflow_service = WorkflowService()
            
            workflow = await workflow_service.get_workflow(
                session=session,
                workflow_id=UUID(workflow_id),
                tenant_id=UUID(current_user["tenant_id"])
            )
            
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workflow not found"
                )
            
            return WorkflowResponse(
                id=str(workflow.id),
                tenant_id=str(workflow.tenant_id),
                name=workflow.name,
                description=workflow.description,
                definition=workflow.definition,
                version=workflow.version,
                status=workflow.status.value,
                is_default=workflow.is_default,
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting workflow: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get workflow"
            )


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    request: WorkflowUpdate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a workflow
    """
    async for session in db:
        try:
            workflow_service = WorkflowService()
            
            workflow_status = None
            if request.status:
                try:
                    workflow_status = WorkflowStatus[request.status.upper()]
                except KeyError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid status: {request.status}"
                    )
            
            workflow = await workflow_service.update_workflow(
                session=session,
                workflow_id=UUID(workflow_id),
                tenant_id=UUID(current_user["tenant_id"]),
                name=request.name,
                description=request.description,
                definition=request.definition,
                status=workflow_status
            )
            
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workflow not found"
                )
            
            return WorkflowResponse(
                id=str(workflow.id),
                tenant_id=str(workflow.tenant_id),
                name=workflow.name,
                description=workflow.description,
                definition=workflow.definition,
                version=workflow.version,
                status=workflow.status.value,
                is_default=workflow.is_default,
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating workflow: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update workflow"
            )


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a workflow
    """
    async for session in db:
        try:
            workflow_service = WorkflowService()
            
            deleted = await workflow_service.delete_workflow(
                session=session,
                workflow_id=UUID(workflow_id),
                tenant_id=UUID(current_user["tenant_id"])
            )
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workflow not found"
                )
            
            return None
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting workflow: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete workflow"
            )
