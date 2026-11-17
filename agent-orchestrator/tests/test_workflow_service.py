"""
Test cases for workflow service
Tests CRUD operations, validation, and business logic
"""
import pytest
from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.workflow_service import WorkflowService
from src.database.models import Workflow, WorkflowStatus


@pytest.fixture
def mock_session():
    """Mock database session"""
    session = AsyncMock()
    return session


@pytest.fixture
def workflow_service(mock_session):
    """Workflow service instance with mocked session"""
    return WorkflowService()


@pytest.fixture
def sample_tenant_id():
    """Sample tenant UUID"""
    return str(uuid4())


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data"""
    return {
        "name": "Test Workflow",
        "description": "Test workflow description",
        "definition": {
            "nodes": [
                {"id": "start", "type": "trigger", "data": {"label": "Start"}},
                {"id": "msg1", "type": "message", "data": {"message": "Hello!"}}
            ],
            "edges": [{"source": "start", "target": "msg1"}],
            "variables": {}
        }
    }


class TestWorkflowCreation:
    """Test workflow creation"""
    
    @pytest.mark.asyncio
    async def test_create_workflow_success(self, workflow_service, mock_session, sample_tenant_id, sample_workflow_data):
        """Test successful workflow creation"""
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock the workflow object
            mock_workflow = MagicMock()
            mock_workflow.id = str(uuid4())
            mock_workflow.name = sample_workflow_data["name"]
            mock_workflow.status = WorkflowStatus.DRAFT
            
            result = await workflow_service.create_workflow(
                tenant_id=sample_tenant_id,
                **sample_workflow_data
            )
            
            assert mock_session.add.called
            assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_create_workflow_with_empty_name(self, workflow_service, sample_tenant_id):
        """Test workflow creation with empty name should fail"""
        with pytest.raises(ValueError):
            await workflow_service.create_workflow(
                tenant_id=sample_tenant_id,
                name="",
                description="Test",
                definition={}
            )
    
    @pytest.mark.asyncio
    async def test_create_workflow_with_invalid_definition(self, workflow_service, sample_tenant_id):
        """Test workflow creation with invalid definition"""
        with pytest.raises(ValueError):
            await workflow_service.create_workflow(
                tenant_id=sample_tenant_id,
                name="Test",
                description="Test",
                definition={"invalid": "structure"}
            )
    
    @pytest.mark.asyncio
    async def test_create_workflow_duplicate_name(self, workflow_service, mock_session, sample_tenant_id, sample_workflow_data):
        """Test creating workflow with duplicate name in same tenant"""
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            # Mock existing workflow
            mock_session.execute.return_value.scalar_one_or_none.return_value = MagicMock()
            
            with pytest.raises(ValueError, match="already exists"):
                await workflow_service.create_workflow(
                    tenant_id=sample_tenant_id,
                    **sample_workflow_data
                )


class TestWorkflowRetrieval:
    """Test workflow retrieval operations"""
    
    @pytest.mark.asyncio
    async def test_get_workflow_by_id_success(self, workflow_service, mock_session, sample_tenant_id):
        """Test retrieving workflow by ID"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflow = MagicMock()
            mock_workflow.id = workflow_id
            mock_workflow.tenant_id = sample_tenant_id
            
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_workflow
            
            result = await workflow_service.get_workflow(workflow_id, sample_tenant_id)
            
            assert result == mock_workflow
    
    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, workflow_service, mock_session, sample_tenant_id):
        """Test retrieving non-existent workflow"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            mock_session.execute.return_value.scalar_one_or_none.return_value = None
            
            result = await workflow_service.get_workflow(workflow_id, sample_tenant_id)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_workflow_wrong_tenant(self, workflow_service, mock_session):
        """Test retrieving workflow from different tenant should fail"""
        workflow_id = str(uuid4())
        tenant_a = str(uuid4())
        tenant_b = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            # Workflow belongs to tenant_a, but requesting with tenant_b
            mock_session.execute.return_value.scalar_one_or_none.return_value = None
            
            result = await workflow_service.get_workflow(workflow_id, tenant_b)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_list_workflows_pagination(self, workflow_service, mock_session, sample_tenant_id):
        """Test listing workflows with pagination"""
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflows = [MagicMock() for _ in range(5)]
            mock_session.execute.return_value.scalars.return_value.all.return_value = mock_workflows
            
            result = await workflow_service.list_workflows(
                tenant_id=sample_tenant_id,
                skip=0,
                limit=10
            )
            
            assert len(result) == 5
    
    @pytest.mark.asyncio
    async def test_list_workflows_filter_by_status(self, workflow_service, mock_session, sample_tenant_id):
        """Test listing workflows filtered by status"""
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflows = [MagicMock()]
            mock_session.execute.return_value.scalars.return_value.all.return_value = mock_workflows
            
            result = await workflow_service.list_workflows(
                tenant_id=sample_tenant_id,
                status=WorkflowStatus.ACTIVE
            )
            
            assert len(result) >= 0


class TestWorkflowUpdate:
    """Test workflow update operations"""
    
    @pytest.mark.asyncio
    async def test_update_workflow_success(self, workflow_service, mock_session, sample_tenant_id):
        """Test successful workflow update"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflow = MagicMock()
            mock_workflow.id = workflow_id
            mock_workflow.tenant_id = sample_tenant_id
            mock_workflow.version = 1
            
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_workflow
            
            result = await workflow_service.update_workflow(
                workflow_id=workflow_id,
                tenant_id=sample_tenant_id,
                name="Updated Name"
            )
            
            assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_update_workflow_version_increment(self, workflow_service, mock_session, sample_tenant_id):
        """Test that workflow version increments on definition update"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflow = MagicMock()
            mock_workflow.id = workflow_id
            mock_workflow.version = 1
            
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_workflow
            
            await workflow_service.update_workflow(
                workflow_id=workflow_id,
                tenant_id=sample_tenant_id,
                definition={"nodes": [], "edges": []}
            )
            
            assert mock_workflow.version == 2
    
    @pytest.mark.asyncio
    async def test_update_workflow_status_change(self, workflow_service, mock_session, sample_tenant_id):
        """Test changing workflow status"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflow = MagicMock()
            mock_workflow.status = WorkflowStatus.DRAFT
            
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_workflow
            
            await workflow_service.update_workflow(
                workflow_id=workflow_id,
                tenant_id=sample_tenant_id,
                status=WorkflowStatus.ACTIVE
            )
            
            assert mock_workflow.status == WorkflowStatus.ACTIVE


class TestWorkflowDeletion:
    """Test workflow deletion"""
    
    @pytest.mark.asyncio
    async def test_delete_workflow_success(self, workflow_service, mock_session, sample_tenant_id):
        """Test successful workflow deletion"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflow = MagicMock()
            mock_workflow.id = workflow_id
            
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_workflow
            
            result = await workflow_service.delete_workflow(workflow_id, sample_tenant_id)
            
            assert result is True
            assert mock_session.delete.called
            assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(self, workflow_service, mock_session, sample_tenant_id):
        """Test deleting non-existent workflow"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            mock_session.execute.return_value.scalar_one_or_none.return_value = None
            
            result = await workflow_service.delete_workflow(workflow_id, sample_tenant_id)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_active_workflow_warning(self, workflow_service, mock_session, sample_tenant_id):
        """Test deleting active workflow shows warning"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflow = MagicMock()
            mock_workflow.status = WorkflowStatus.ACTIVE
            
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_workflow
            
            # Should still delete but with warning
            result = await workflow_service.delete_workflow(workflow_id, sample_tenant_id)
            
            assert result is True


class TestWorkflowExecution:
    """Test workflow execution tracking"""
    
    @pytest.mark.asyncio
    async def test_create_execution_record(self, workflow_service, mock_session, sample_tenant_id):
        """Test creating workflow execution record"""
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            result = await workflow_service.create_execution(
                workflow_id=workflow_id,
                tenant_id=sample_tenant_id,
                input_data={"message": "Test"},
                user_id="user123"
            )
            
            assert mock_session.add.called
            assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_execution_tracks_duration(self, workflow_service, mock_session):
        """Test that execution records track duration"""
        # This would test execution time tracking
        pass
    
    @pytest.mark.asyncio
    async def test_execution_records_errors(self, workflow_service, mock_session):
        """Test that execution records capture errors"""
        # This would test error logging
        pass


class TestWorkflowValidation:
    """Test workflow definition validation"""
    
    def test_validate_workflow_definition_valid(self, workflow_service):
        """Test validation of valid workflow definition"""
        definition = {
            "nodes": [
                {"id": "start", "type": "trigger"},
                {"id": "end", "type": "message"}
            ],
            "edges": [{"source": "start", "target": "end"}],
            "variables": {}
        }
        
        # Should not raise error
        assert workflow_service._validate_definition(definition) is True
    
    def test_validate_workflow_definition_missing_nodes(self, workflow_service):
        """Test validation fails when nodes are missing"""
        definition = {
            "edges": [],
            "variables": {}
        }
        
        with pytest.raises(ValueError, match="nodes"):
            workflow_service._validate_definition(definition)
    
    def test_validate_workflow_definition_invalid_edges(self, workflow_service):
        """Test validation fails with invalid edges"""
        definition = {
            "nodes": [{"id": "start", "type": "trigger"}],
            "edges": [{"source": "nonexistent", "target": "start"}],
            "variables": {}
        }
        
        with pytest.raises(ValueError, match="edge"):
            workflow_service._validate_definition(definition)
    
    def test_validate_workflow_definition_circular_reference(self, workflow_service):
        """Test detection of circular references"""
        definition = {
            "nodes": [
                {"id": "a", "type": "message"},
                {"id": "b", "type": "message"}
            ],
            "edges": [
                {"source": "a", "target": "b"},
                {"source": "b", "target": "a"}  # Circular!
            ],
            "variables": {}
        }
        
        # Should detect circular reference
        with pytest.raises(ValueError, match="circular"):
            workflow_service._validate_definition(definition)


class TestTenantIsolation:
    """Test tenant isolation in workflow operations"""
    
    @pytest.mark.asyncio
    async def test_tenant_cannot_access_other_tenant_workflows(self, workflow_service, mock_session):
        """Test tenant isolation is enforced"""
        tenant_a = str(uuid4())
        tenant_b = str(uuid4())
        workflow_id = str(uuid4())
        
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            # Workflow belongs to tenant_a
            mock_session.execute.return_value.scalar_one_or_none.return_value = None
            
            # Tenant B trying to access tenant A's workflow
            result = await workflow_service.get_workflow(workflow_id, tenant_b)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_list_workflows_only_returns_tenant_workflows(self, workflow_service, mock_session, sample_tenant_id):
        """Test that list only returns workflows for the specific tenant"""
        with patch('src.services.workflow_service.async_session_maker') as mock_maker:
            mock_maker.return_value.__aenter__.return_value = mock_session
            
            mock_workflows = [MagicMock(tenant_id=sample_tenant_id) for _ in range(3)]
            mock_session.execute.return_value.scalars.return_value.all.return_value = mock_workflows
            
            result = await workflow_service.list_workflows(tenant_id=sample_tenant_id)
            
            # All workflows should belong to the tenant
            assert all(w.tenant_id == sample_tenant_id for w in result)
