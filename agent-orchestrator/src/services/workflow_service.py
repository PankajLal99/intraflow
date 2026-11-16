"""
Workflow service for managing workflows
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Workflow, WorkflowStatus, WorkflowExecution

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for workflow CRUD operations"""
    
    async def create_workflow(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        name: str,
        definition: Dict[str, Any],
        description: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> Workflow:
        """
        Create a new workflow
        
        Args:
            session: Database session
            tenant_id: Tenant UUID
            name: Workflow name
            definition: Workflow definition (JSON)
            description: Optional description
            created_by: User UUID who created it
            
        Returns:
            Created Workflow
        """
        try:
            workflow = Workflow(
                tenant_id=tenant_id,
                name=name,
                description=description,
                definition=definition,
                status=WorkflowStatus.DRAFT,
                created_by=created_by
            )
            
            session.add(workflow)
            await session.commit()
            await session.refresh(workflow)
            
            logger.info(f"Created workflow {workflow.id} for tenant {tenant_id}")
            
            return workflow
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating workflow: {str(e)}", exc_info=True)
            raise
    
    async def get_workflow(
        self,
        session: AsyncSession,
        workflow_id: UUID,
        tenant_id: UUID
    ) -> Optional[Workflow]:
        """
        Get workflow by ID (tenant-scoped)
        
        Args:
            session: Database session
            workflow_id: Workflow UUID
            tenant_id: Tenant UUID
            
        Returns:
            Workflow or None
        """
        try:
            stmt = select(Workflow).where(
                and_(
                    Workflow.id == workflow_id,
                    Workflow.tenant_id == tenant_id
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting workflow: {str(e)}", exc_info=True)
            raise
    
    async def list_workflows(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        status: Optional[WorkflowStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Workflow]:
        """
        List workflows for a tenant
        
        Args:
            session: Database session
            tenant_id: Tenant UUID
            status: Optional status filter
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of Workflows
        """
        try:
            stmt = select(Workflow).where(Workflow.tenant_id == tenant_id)
            
            if status:
                stmt = stmt.where(Workflow.status == status)
            
            stmt = stmt.order_by(Workflow.updated_at.desc())
            stmt = stmt.limit(limit).offset(offset)
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error listing workflows: {str(e)}", exc_info=True)
            raise
    
    async def update_workflow(
        self,
        session: AsyncSession,
        workflow_id: UUID,
        tenant_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        definition: Optional[Dict[str, Any]] = None,
        status: Optional[WorkflowStatus] = None
    ) -> Optional[Workflow]:
        """
        Update workflow (tenant-scoped)
        
        Args:
            session: Database session
            workflow_id: Workflow UUID
            tenant_id: Tenant UUID
            name: Optional new name
            description: Optional new description
            definition: Optional new definition
            status: Optional new status
            
        Returns:
            Updated Workflow or None
        """
        try:
            workflow = await self.get_workflow(session, workflow_id, tenant_id)
            
            if not workflow:
                return None
            
            if name is not None:
                workflow.name = name
            if description is not None:
                workflow.description = description
            if definition is not None:
                workflow.definition = definition
                workflow.version += 1
            if status is not None:
                workflow.status = status
            
            await session.commit()
            await session.refresh(workflow)
            
            logger.info(f"Updated workflow {workflow_id}")
            
            return workflow
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating workflow: {str(e)}", exc_info=True)
            raise
    
    async def delete_workflow(
        self,
        session: AsyncSession,
        workflow_id: UUID,
        tenant_id: UUID
    ) -> bool:
        """
        Delete workflow (tenant-scoped)
        
        Args:
            session: Database session
            workflow_id: Workflow UUID
            tenant_id: Tenant UUID
            
        Returns:
            True if deleted
        """
        try:
            workflow = await self.get_workflow(session, workflow_id, tenant_id)
            
            if not workflow:
                return False
            
            await session.delete(workflow)
            await session.commit()
            
            logger.info(f"Deleted workflow {workflow_id}")
            
            return True
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting workflow: {str(e)}", exc_info=True)
            raise
    
    async def get_active_workflow(
        self,
        session: AsyncSession,
        tenant_id: UUID
    ) -> Optional[Workflow]:
        """
        Get the active (or default) workflow for a tenant
        
        Args:
            session: Database session
            tenant_id: Tenant UUID
            
        Returns:
            Active Workflow or None
        """
        try:
            stmt = select(Workflow).where(
                and_(
                    Workflow.tenant_id == tenant_id,
                    Workflow.status == WorkflowStatus.ACTIVE,
                    Workflow.is_default == True
                )
            )
            result = await session.execute(stmt)
            workflow = result.scalar_one_or_none()
            
            if not workflow:
                stmt = select(Workflow).where(
                    and_(
                        Workflow.tenant_id == tenant_id,
                        Workflow.status == WorkflowStatus.ACTIVE
                    )
                ).order_by(Workflow.updated_at.desc())
                result = await session.execute(stmt)
                workflow = result.scalars().first()
            
            return workflow
            
        except Exception as e:
            logger.error(f"Error getting active workflow: {str(e)}", exc_info=True)
            raise
    
    async def create_execution(
        self,
        session: AsyncSession,
        workflow_id: UUID,
        tenant_id: UUID,
        conversation_id: Optional[UUID] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        Create a new workflow execution
        
        Args:
            session: Database session
            workflow_id: Workflow UUID
            tenant_id: Tenant UUID
            conversation_id: Optional conversation UUID
            context: Optional execution context
            
        Returns:
            Created WorkflowExecution
        """
        try:
            execution = WorkflowExecution(
                tenant_id=tenant_id,
                workflow_id=workflow_id,
                conversation_id=conversation_id,
                context=context or {},
                execution_log=[],
                status="running"
            )
            
            session.add(execution)
            await session.commit()
            await session.refresh(execution)
            
            logger.info(f"Created workflow execution {execution.id}")
            
            return execution
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating execution: {str(e)}", exc_info=True)
            raise
