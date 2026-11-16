"""
Workflow Execution Engine
Executes visual workflows defined by users
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from enum import Enum

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    """Node types in workflow"""
    TRIGGER = "trigger"
    ACTION = "action"
    LOGIC = "logic"
    INTEGRATION = "integration"


class NodeSubtype(str, Enum):
    """Node subtypes"""
    # Triggers
    MESSAGE_RECEIVED = "message_received"
    BUTTON_CLICKED = "button_clicked"
    
    # Actions
    SEND_MESSAGE = "send_message"
    SEND_BUTTONS = "send_buttons"
    SEND_LIST = "send_list"
    API_CALL = "api_call"
    DELAY = "delay"
    SET_VARIABLE = "set_variable"
    
    # Logic
    CONDITION = "condition"
    SWITCH = "switch"
    AI_CLASSIFIER = "ai_classifier"
    REGEX_MATCH = "regex_match"


class ExecutionStatus(str, Enum):
    """Execution status"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class WorkflowNode:
    """Represents a workflow node"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.type = NodeType(data['type'])
        self.subtype = NodeSubtype(data['subtype'])
        self.config = data.get('config', {})
        self.position = data.get('position', {})
        
    def __repr__(self):
        return f"<Node {self.id} ({self.type}/{self.subtype})>"


class WorkflowEdge:
    """Represents a workflow edge/connection"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.source = data['source']
        self.target = data['target']
        self.condition = data.get('condition')
        self.label = data.get('label')
        
    def __repr__(self):
        return f"<Edge {self.source} -> {self.target}>"


class Workflow:
    """Represents a complete workflow"""
    
    def __init__(self, definition: Dict[str, Any]):
        self.id = definition.get('id')
        self.name = definition.get('name')
        self.nodes = [WorkflowNode(n) for n in definition.get('nodes', [])]
        self.edges = [WorkflowEdge(e) for e in definition.get('edges', [])]
        self.variables = definition.get('variables', {})
        self.settings = definition.get('settings', {})
        
        # Build node lookup
        self.nodes_map = {n.id: n for n in self.nodes}
        
        # Build edge lookup (source -> [targets])
        self.edges_map: Dict[str, List[WorkflowEdge]] = {}
        for edge in self.edges:
            if edge.source not in self.edges_map:
                self.edges_map[edge.source] = []
            self.edges_map[edge.source].append(edge)
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Get node by ID"""
        return self.nodes_map.get(node_id)
    
    def get_next_nodes(self, node_id: str) -> List[WorkflowEdge]:
        """Get all edges from a node"""
        return self.edges_map.get(node_id, [])
    
    def get_start_node(self) -> Optional[WorkflowNode]:
        """Get the starting node (first trigger)"""
        for node in self.nodes:
            if node.type == NodeType.TRIGGER:
                return node
        return None


class WorkflowExecutor:
    """
    Executes a workflow for a conversation
    """
    
    def __init__(
        self,
        workflow: Workflow,
        conversation_id: str,
        tenant_id: str,
        llm=None
    ):
        self.workflow = workflow
        self.conversation_id = conversation_id
        self.tenant_id = tenant_id
        self.llm = llm
        
        # Execution state
        self.context: Dict[str, Any] = workflow.variables.copy()
        self.current_node_id: Optional[str] = None
        self.execution_log: List[Dict[str, Any]] = []
        self.status = ExecutionStatus.RUNNING
        
        # Start from the first node
        start_node = workflow.get_start_node()
        if start_node:
            self.current_node_id = start_node.id
    
    async def execute(self, user_input: str) -> Dict[str, Any]:
        """
        Execute workflow with user input
        Returns response to send to user
        """
        try:
            # Update context with user input
            self.context['user_message'] = user_input
            self.context['timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Executing workflow {self.workflow.id} from node {self.current_node_id}")
            
            # Get current node
            node = self.workflow.get_node(self.current_node_id)
            if not node:
                raise ValueError(f"Node {self.current_node_id} not found")
            
            # Execute node
            result = await self.execute_node(node)
            
            # Log execution
            self.log_execution(node, result)
            
            # Determine next node
            next_node = await self.determine_next_node(node, result)
            self.current_node_id = next_node.id if next_node else None
            
            # Check if workflow completed
            if self.current_node_id is None:
                self.status = ExecutionStatus.COMPLETED
                logger.info(f"Workflow {self.workflow.id} completed")
            
            return {
                'success': True,
                'response': result.get('response', ''),
                'buttons': result.get('buttons'),
                'next_node': self.current_node_id,
                'status': self.status.value,
                'context': self.context
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            self.status = ExecutionStatus.FAILED
            self.log_execution(node, {'error': str(e)})
            
            return {
                'success': False,
                'response': self.workflow.settings.get(
                    'fallback_message',
                    'Sorry, something went wrong. Please try again.'
                ),
                'error': str(e),
                'status': self.status.value
            }
    
    async def execute_node(self, node: WorkflowNode) -> Dict[str, Any]:
        """Execute a specific node"""
        
        logger.info(f"Executing node {node.id} ({node.type}/{node.subtype})")
        
        if node.type == NodeType.ACTION:
            return await self.execute_action_node(node)
        elif node.type == NodeType.LOGIC:
            return await self.execute_logic_node(node)
        elif node.type == NodeType.TRIGGER:
            return await self.execute_trigger_node(node)
        else:
            raise ValueError(f"Unknown node type: {node.type}")
    
    async def execute_action_node(self, node: WorkflowNode) -> Dict[str, Any]:
        """Execute action nodes"""
        
        if node.subtype == NodeSubtype.SEND_MESSAGE:
            message = self.interpolate(node.config.get('message', ''))
            return {
                'response': message,
                'type': 'message'
            }
        
        elif node.subtype == NodeSubtype.SEND_BUTTONS:
            message = self.interpolate(node.config.get('message', ''))
            buttons = node.config.get('buttons', [])
            return {
                'response': message,
                'buttons': buttons,
                'type': 'buttons'
            }
        
        elif node.subtype == NodeSubtype.SET_VARIABLE:
            var_name = node.config.get('variable')
            var_value = self.interpolate(node.config.get('value', ''))
            self.context[var_name] = var_value
            return {
                'type': 'variable_set',
                'variable': var_name,
                'value': var_value
            }
        
        elif node.subtype == NodeSubtype.API_CALL:
            # TODO: Implement API calling
            return {
                'response': 'API call not yet implemented',
                'type': 'api_call'
            }
        
        else:
            raise ValueError(f"Unknown action subtype: {node.subtype}")
    
    async def execute_logic_node(self, node: WorkflowNode) -> Dict[str, Any]:
        """Execute logic nodes"""
        
        if node.subtype == NodeSubtype.CONDITION:
            # Evaluate condition
            variable = self.context.get(node.config.get('variable'))
            operator = node.config.get('operator', 'equals')
            value = node.config.get('value')
            
            result = self.evaluate_condition(variable, operator, value)
            
            return {
                'type': 'condition',
                'result': result,
                'true_branch': node.config.get('true_branch'),
                'false_branch': node.config.get('false_branch')
            }
        
        elif node.subtype == NodeSubtype.AI_CLASSIFIER:
            # Use LLM to classify
            if not self.llm:
                raise ValueError("LLM not configured for AI classification")
            
            prompt = self.interpolate(node.config.get('prompt', ''))
            categories = node.config.get('categories', [])
            
            # TODO: Call LLM for classification
            classification = categories[0] if categories else 'unknown'
            
            self.context['classification'] = classification
            
            return {
                'type': 'ai_classification',
                'classification': classification,
                'categories': categories
            }
        
        else:
            raise ValueError(f"Unknown logic subtype: {node.subtype}")
    
    async def execute_trigger_node(self, node: WorkflowNode) -> Dict[str, Any]:
        """Execute trigger nodes (usually just pass through)"""
        return {
            'type': 'trigger',
            'triggered': True
        }
    
    def evaluate_condition(self, variable: Any, operator: str, value: Any) -> bool:
        """Evaluate a condition"""
        
        if operator == 'equals':
            return variable == value
        elif operator == 'not_equals':
            return variable != value
        elif operator == 'contains':
            return value in str(variable)
        elif operator == 'greater_than':
            return float(variable) > float(value)
        elif operator == 'less_than':
            return float(variable) < float(value)
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    async def determine_next_node(
        self,
        current_node: WorkflowNode,
        result: Dict[str, Any]
    ) -> Optional[WorkflowNode]:
        """Determine the next node to execute"""
        
        edges = self.workflow.get_next_nodes(current_node.id)
        
        if not edges:
            # End of workflow
            return None
        
        # For logic nodes with branches
        if result.get('type') == 'condition':
            if result['result']:
                next_id = result.get('true_branch')
            else:
                next_id = result.get('false_branch')
            
            return self.workflow.get_node(next_id) if next_id else None
        
        # Default: take first edge
        if edges:
            return self.workflow.get_node(edges[0].target)
        
        return None
    
    def interpolate(self, text: str) -> str:
        """
        Interpolate variables in text
        Example: "Hello {{user_name}}" -> "Hello John"
        """
        result = text
        for key, value in self.context.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result
    
    def log_execution(self, node: WorkflowNode, result: Dict[str, Any]):
        """Log node execution"""
        self.execution_log.append({
            'node_id': node.id,
            'node_type': node.type.value,
            'node_subtype': node.subtype.value,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_state(self) -> Dict[str, Any]:
        """Get current execution state for persistence"""
        return {
            'conversation_id': self.conversation_id,
            'workflow_id': self.workflow.id,
            'current_node_id': self.current_node_id,
            'context': self.context,
            'execution_log': self.execution_log,
            'status': self.status.value
        }


# Example usage
async def example_workflow():
    """Example of creating and executing a workflow"""
    
    # Define a simple workflow
    workflow_definition = {
        'id': 'wf_example',
        'name': 'Welcome Flow',
        'nodes': [
            {
                'id': 'trigger_1',
                'type': 'trigger',
                'subtype': 'message_received',
                'config': {}
            },
            {
                'id': 'action_1',
                'type': 'action',
                'subtype': 'send_message',
                'config': {
                    'message': 'Hello! What can I help you with today?'
                }
            },
            {
                'id': 'action_2',
                'type': 'action',
                'subtype': 'send_buttons',
                'config': {
                    'message': 'Please choose an option:',
                    'buttons': [
                        {'id': 'btn_1', 'text': 'Products'},
                        {'id': 'btn_2', 'text': 'Support'},
                        {'id': 'btn_3', 'text': 'Pricing'}
                    ]
                }
            }
        ],
        'edges': [
            {'id': 'e1', 'source': 'trigger_1', 'target': 'action_1'},
            {'id': 'e2', 'source': 'action_1', 'target': 'action_2'}
        ],
        'variables': {},
        'settings': {
            'timeout_seconds': 300,
            'fallback_message': 'Sorry, I didn\'t understand.'
        }
    }
    
    # Create workflow
    workflow = Workflow(workflow_definition)
    
    # Create executor
    executor = WorkflowExecutor(
        workflow=workflow,
        conversation_id='conv_123',
        tenant_id='tenant_abc'
    )
    
    # Execute with user input
    result = await executor.execute('Hello')
    
    print(f"Response: {result['response']}")
    print(f"Buttons: {result.get('buttons')}")
    print(f"Status: {result['status']}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(example_workflow())
