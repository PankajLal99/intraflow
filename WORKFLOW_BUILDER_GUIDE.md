# Workflow Builder Implementation Guide

## Overview

This guide explains how to implement the **Visual Workflow Builder** for your WhatsApp SaaS platform, allowing users to create custom conversation flows without coding.

## Table of Contents
1. [Architecture](#architecture)
2. [Frontend Implementation](#frontend-implementation)
3. [Backend Integration](#backend-integration)
4. [Node Types Reference](#node-types-reference)
5. [Testing Workflows](#testing-workflows)

---

## 1. Architecture

### Component Overview

```
┌────────────────────────────────────────────────────────┐
│          Workflow Builder (React Frontend)              │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐     │
│  │ Node Palette │  │   Canvas   │  │ Properties │     │
│  │  (Drag)      │  │  (Drop)    │  │   Panel    │     │
│  └──────────────┘  └────────────┘  └────────────┘     │
│                          │                             │
│                          │ Save/Publish                │
│                          ▼                             │
│                  [Workflow API]                        │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│         Backend (FastAPI + PostgreSQL)                 │
│  ┌──────────────────────────────────────────┐          │
│  │  Workflow Definition (JSON)              │          │
│  │  - Nodes (Actions, Logic, Triggers)      │          │
│  │  - Edges (Connections)                   │          │
│  │  - Variables                             │          │
│  └──────────────────────────────────────────┘          │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│           Workflow Executor (Python)                   │
│  ┌──────────────────────────────────────────┐          │
│  │  Runtime Execution                       │          │
│  │  - State Machine                         │          │
│  │  - Node Execution                        │          │
│  │  - Context Management                    │          │
│  └──────────────────────────────────────────┘          │
└────────────────────────────────────────────────────────┘
```

---

## 2. Frontend Implementation

### 2.1 Technology Stack

```json
{
  "framework": "React 18 + TypeScript",
  "flowEditor": "React Flow",
  "ui": "shadcn/ui + Tailwind CSS",
  "state": "Zustand",
  "forms": "React Hook Form",
  "api": "Axios"
}
```

### 2.2 Project Structure

```
workflow-builder/
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── WorkflowBuilder/
│   │   │   │   ├── Canvas.tsx          # Main canvas with React Flow
│   │   │   │   ├── NodePalette.tsx     # Draggable nodes
│   │   │   │   ├── PropertiesPanel.tsx # Node configuration
│   │   │   │   ├── Toolbar.tsx         # Save, test, publish
│   │   │   │   └── nodes/
│   │   │   │       ├── SendMessageNode.tsx
│   │   │   │       ├── ConditionNode.tsx
│   │   │   │       ├── AIClassifierNode.tsx
│   │   │   │       └── ...
│   │   │   └── Dashboard/
│   │   │       ├── WorkflowList.tsx
│   │   │       ├── Analytics.tsx
│   │   │       └── Settings.tsx
│   │   ├── stores/
│   │   │   └── workflowStore.ts        # Zustand store
│   │   ├── api/
│   │   │   └── workflows.ts            # API calls
│   │   ├── types/
│   │   │   └── workflow.ts             # TypeScript types
│   │   └── utils/
│   │       └── validation.ts
│   └── public/
└── backend/
    └── (see backend section)
```

### 2.3 Install Dependencies

```bash
cd workflow-builder/frontend

npm init -y

npm install react react-dom react-router-dom
npm install reactflow @reactflow/node-resizer
npm install zustand axios react-hook-form zod
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install tailwindcss postcss autoprefixer
npm install @types/react @types/node typescript
npm install vite @vitejs/plugin-react

npx tailwindcss init -p
```

### 2.4 Sample Code: Canvas Component

```typescript
// src/components/WorkflowBuilder/Canvas.tsx
import React, { useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Connection,
  Edge,
  Node,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { useWorkflowStore } from '../../stores/workflowStore';
import SendMessageNode from './nodes/SendMessageNode';
import ConditionNode from './nodes/ConditionNode';
import AIClassifierNode from './nodes/AIClassifierNode';

// Custom node types
const nodeTypes = {
  sendMessage: SendMessageNode,
  condition: ConditionNode,
  aiClassifier: AIClassifierNode,
};

export const Canvas: React.FC = () => {
  const { nodes, edges, setNodes, setEdges, selectedNode, setSelectedNode } = 
    useWorkflowStore();

  const [nodesState, setNodesState, onNodesChange] = useNodesState(nodes);
  const [edgesState, setEdgesState, onEdgesChange] = useEdgesState(edges);

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds));
    },
    [setEdges]
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      setSelectedNode(node);
    },
    [setSelectedNode]
  );

  return (
    <div className="h-screen w-full">
      <ReactFlow
        nodes={nodesState}
        edges={edgesState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
};
```

### 2.5 Sample Code: Send Message Node

```typescript
// src/components/WorkflowBuilder/nodes/SendMessageNode.tsx
import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface SendMessageNodeData {
  message: string;
  buttons?: Array<{ id: string; text: string }>;
}

const SendMessageNode: React.FC<NodeProps<SendMessageNodeData>> = ({ data, selected }) => {
  return (
    <div className={`relative ${selected ? 'ring-2 ring-blue-500' : ''}`}>
      <Handle type="target" position={Position.Top} />
      
      <Card className="w-64 shadow-lg">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Send Message
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-gray-600">
            {data.message ? (
              <p className="line-clamp-2">{data.message}</p>
            ) : (
              <p className="italic">No message set</p>
            )}
          </div>
          {data.buttons && data.buttons.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-500">
                {data.buttons.length} button(s)
              </p>
            </div>
          )}
        </CardContent>
      </Card>
      
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

export default memo(SendMessageNode);
```

### 2.6 Sample Code: Node Palette

```typescript
// src/components/WorkflowBuilder/NodePalette.tsx
import React from 'react';
import { MessageSquare, GitBranch, Zap, Brain } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface NodeTemplate {
  id: string;
  type: string;
  label: string;
  icon: React.ReactNode;
  defaultData: any;
}

const nodeTemplates: NodeTemplate[] = [
  {
    id: 'send-message',
    type: 'sendMessage',
    label: 'Send Message',
    icon: <MessageSquare className="h-4 w-4" />,
    defaultData: { message: '' },
  },
  {
    id: 'condition',
    type: 'condition',
    label: 'Condition',
    icon: <GitBranch className="h-4 w-4" />,
    defaultData: { variable: '', operator: 'equals', value: '' },
  },
  {
    id: 'ai-classifier',
    type: 'aiClassifier',
    label: 'AI Classifier',
    icon: <Brain className="h-4 w-4" />,
    defaultData: { prompt: '', categories: [] },
  },
];

export const NodePalette: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeTemplate: NodeTemplate) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(nodeTemplate));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Card className="w-64 h-full overflow-y-auto">
      <CardHeader>
        <CardTitle>Nodes</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Actions</p>
          {nodeTemplates
            .filter((t) => t.type.includes('send') || t.type.includes('api'))
            .map((template) => (
              <div
                key={template.id}
                draggable
                onDragStart={(e) => onDragStart(e, template)}
                className="p-3 border rounded-lg cursor-move hover:bg-gray-50 flex items-center gap-2"
              >
                {template.icon}
                <span className="text-sm">{template.label}</span>
              </div>
            ))}
        </div>

        <div className="space-y-2 mt-4">
          <p className="text-sm font-medium text-gray-700">Logic</p>
          {nodeTemplates
            .filter((t) => t.type.includes('condition') || t.type.includes('ai'))
            .map((template) => (
              <div
                key={template.id}
                draggable
                onDragStart={(e) => onDragStart(e, template)}
                className="p-3 border rounded-lg cursor-move hover:bg-gray-50 flex items-center gap-2"
              >
                {template.icon}
                <span className="text-sm">{template.label}</span>
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  );
};
```

### 2.7 Sample Code: Zustand Store

```typescript
// src/stores/workflowStore.ts
import { create } from 'zustand';
import { Node, Edge } from 'reactflow';

interface WorkflowStore {
  // Workflow data
  workflowId: string | null;
  workflowName: string;
  nodes: Node[];
  edges: Edge[];
  selectedNode: Node | null;
  
  // Actions
  setWorkflowId: (id: string) => void;
  setWorkflowName: (name: string) => void;
  setNodes: (nodes: Node[] | ((nodes: Node[]) => Node[])) => void;
  setEdges: (edges: Edge[] | ((edges: Edge[]) => Edge[])) => void;
  setSelectedNode: (node: Node | null) => void;
  addNode: (node: Node) => void;
  updateNode: (nodeId: string, data: any) => void;
  deleteNode: (nodeId: string) => void;
  clearWorkflow: () => void;
}

export const useWorkflowStore = create<WorkflowStore>((set) => ({
  workflowId: null,
  workflowName: 'Untitled Workflow',
  nodes: [],
  edges: [],
  selectedNode: null,
  
  setWorkflowId: (id) => set({ workflowId: id }),
  setWorkflowName: (name) => set({ workflowName: name }),
  setNodes: (nodes) => 
    set((state) => ({
      nodes: typeof nodes === 'function' ? nodes(state.nodes) : nodes,
    })),
  setEdges: (edges) =>
    set((state) => ({
      edges: typeof edges === 'function' ? edges(state.edges) : edges,
    })),
  setSelectedNode: (node) => set({ selectedNode: node }),
  
  addNode: (node) =>
    set((state) => ({
      nodes: [...state.nodes, node],
    })),
  
  updateNode: (nodeId, data) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
      ),
    })),
  
  deleteNode: (nodeId) =>
    set((state) => ({
      nodes: state.nodes.filter((n) => n.id !== nodeId),
      edges: state.edges.filter((e) => e.source !== nodeId && e.target !== nodeId),
    })),
  
  clearWorkflow: () =>
    set({
      nodes: [],
      edges: [],
      selectedNode: null,
      workflowName: 'Untitled Workflow',
    }),
}));
```

---

## 3. Backend Integration

### 3.1 API Endpoints

```python
# agent-orchestrator/src/api/workflow_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from src.models.workflow import Workflow, WorkflowCreate, WorkflowUpdate
from src.services.workflow_service import WorkflowService
from src.api.dependencies import get_current_tenant

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=List[Workflow])
async def list_workflows(
    tenant_id: UUID = Depends(get_current_tenant),
    skip: int = 0,
    limit: int = 100
):
    """List all workflows for tenant"""
    service = WorkflowService()
    return await service.list_workflows(tenant_id, skip, limit)


@router.post("/", response_model=Workflow)
async def create_workflow(
    workflow: WorkflowCreate,
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Create a new workflow"""
    service = WorkflowService()
    return await service.create_workflow(tenant_id, workflow)


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(
    workflow_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Get workflow by ID"""
    service = WorkflowService()
    workflow = await service.get_workflow(tenant_id, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/{workflow_id}", response_model=Workflow)
async def update_workflow(
    workflow_id: UUID,
    workflow_update: WorkflowUpdate,
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Update workflow"""
    service = WorkflowService()
    workflow = await service.update_workflow(tenant_id, workflow_id, workflow_update)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/{workflow_id}/publish")
async def publish_workflow(
    workflow_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Publish workflow (make it active)"""
    service = WorkflowService()
    result = await service.publish_workflow(tenant_id, workflow_id)
    return {"success": True, "workflow_id": workflow_id, "status": "active"}


@router.post("/{workflow_id}/test")
async def test_workflow(
    workflow_id: UUID,
    test_input: str,
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Test workflow with sample input"""
    service = WorkflowService()
    result = await service.test_workflow(tenant_id, workflow_id, test_input)
    return result


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Delete workflow"""
    service = WorkflowService()
    await service.delete_workflow(tenant_id, workflow_id)
    return {"success": True, "workflow_id": workflow_id}
```

### 3.2 Workflow Service

```python
# agent-orchestrator/src/services/workflow_service.py
from typing import List, Optional
from uuid import UUID
import json

from src.models.workflow import Workflow, WorkflowCreate, WorkflowUpdate
from src.workflow.executor import WorkflowExecutor, Workflow as WorkflowDef
from src.database import get_db

class WorkflowService:
    """Service for managing workflows"""
    
    async def create_workflow(
        self,
        tenant_id: UUID,
        workflow_data: WorkflowCreate
    ) -> Workflow:
        """Create new workflow"""
        # Save to database
        async with get_db() as db:
            workflow = await db.workflows.create({
                'tenant_id': tenant_id,
                'name': workflow_data.name,
                'description': workflow_data.description,
                'definition': workflow_data.definition,
                'status': 'draft'
            })
            return workflow
    
    async def update_workflow(
        self,
        tenant_id: UUID,
        workflow_id: UUID,
        workflow_update: WorkflowUpdate
    ) -> Optional[Workflow]:
        """Update workflow"""
        async with get_db() as db:
            workflow = await db.workflows.update(
                workflow_id,
                tenant_id=tenant_id,
                data=workflow_update.dict(exclude_unset=True)
            )
            return workflow
    
    async def publish_workflow(
        self,
        tenant_id: UUID,
        workflow_id: UUID
    ) -> Workflow:
        """Publish workflow (activate it)"""
        async with get_db() as db:
            workflow = await db.workflows.update(
                workflow_id,
                tenant_id=tenant_id,
                data={'status': 'active'}
            )
            return workflow
    
    async def test_workflow(
        self,
        tenant_id: UUID,
        workflow_id: UUID,
        test_input: str
    ) -> dict:
        """Test workflow execution"""
        # Load workflow
        async with get_db() as db:
            workflow_data = await db.workflows.get(workflow_id, tenant_id=tenant_id)
        
        # Create executor
        workflow = WorkflowDef(workflow_data.definition)
        executor = WorkflowExecutor(
            workflow=workflow,
            conversation_id='test',
            tenant_id=str(tenant_id)
        )
        
        # Execute
        result = await executor.execute(test_input)
        return result
```

---

## 4. Node Types Reference

### 4.1 Action Nodes

#### Send Message
```json
{
  "type": "action",
  "subtype": "send_message",
  "config": {
    "message": "Hello {{user_name}}!"
  }
}
```

#### Send Buttons
```json
{
  "type": "action",
  "subtype": "send_buttons",
  "config": {
    "message": "Choose an option:",
    "buttons": [
      {"id": "btn_1", "text": "Option 1"},
      {"id": "btn_2", "text": "Option 2"}
    ]
  }
}
```

#### API Call
```json
{
  "type": "action",
  "subtype": "api_call",
  "config": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer {{api_key}}"
    },
    "response_variable": "api_response"
  }
}
```

### 4.2 Logic Nodes

#### Condition
```json
{
  "type": "logic",
  "subtype": "condition",
  "config": {
    "variable": "user_type",
    "operator": "equals",
    "value": "premium",
    "true_branch": "node_id_1",
    "false_branch": "node_id_2"
  }
}
```

#### AI Classifier
```json
{
  "type": "logic",
  "subtype": "ai_classifier",
  "config": {
    "prompt": "Classify this message: {{user_message}}",
    "categories": ["sales", "support", "billing"],
    "model": "gpt-4o-mini"
  }
}
```

---

## 5. Testing Workflows

### 5.1 Test Mode UI

Add a "Test" button that opens a chat simulator:

```
┌────────────────────────────────────────┐
│  Test Workflow: Lead Qualification     │
├────────────────────────────────────────┤
│                                        │
│  [Chat Simulator]                      │
│  ┌──────────────────────────────────┐  │
│  │ Bot: Hello! How can I help?     │  │
│  │                                  │  │
│  │ You: I need a laptop            │  │
│  │                                  │  │
│  │ Bot: Great! We have...          │  │
│  └──────────────────────────────────┘  │
│                                        │
│  Type message: [___________________]   │
│  [Send]                                │
│                                        │
│  [Execution Log]                       │
│  ├─ ✓ Node: Start                     │
│  ├─ ✓ Node: Send Welcome (200ms)      │
│  └─ → Node: AI Classify (running...)  │
└────────────────────────────────────────┘
```

### 5.2 Test API Endpoint

```python
@router.post("/{workflow_id}/test")
async def test_workflow(
    workflow_id: UUID,
    test_data: WorkflowTestRequest,
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Test workflow in simulation mode"""
    
    # Load workflow
    workflow = await get_workflow(tenant_id, workflow_id)
    
    # Create test executor
    executor = WorkflowExecutor(
        workflow=Workflow(workflow.definition),
        conversation_id='test',
        tenant_id=str(tenant_id),
        test_mode=True  # Don't actually send WhatsApp messages
    )
    
    # Execute
    result = await executor.execute(test_data.input)
    
    return {
        'success': True,
        'response': result['response'],
        'execution_log': executor.execution_log,
        'context': executor.context
    }
```

---

## Next Steps

### Phase 1: Core Implementation (Week 1-2)
- [ ] Set up React app with React Flow
- [ ] Implement basic nodes (Send Message, Condition)
- [ ] Create node palette and canvas
- [ ] Implement save/load functionality
- [ ] Add backend API endpoints

### Phase 2: Advanced Nodes (Week 3-4)
- [ ] Add AI Classifier node
- [ ] Add API Call node
- [ ] Add button and list nodes
- [ ] Implement variable interpolation
- [ ] Add delay and set variable nodes

### Phase 3: Testing & Polish (Week 5-6)
- [ ] Build test simulator
- [ ] Add workflow templates
- [ ] Implement version control
- [ ] Add analytics dashboard
- [ ] Error handling and validation

### Phase 4: Production (Week 7-8)
- [ ] User onboarding flow
- [ ] Documentation
- [ ] Performance optimization
- [ ] Deploy to production

---

## Resources

- **React Flow Docs**: https://reactflow.dev/
- **shadcn/ui**: https://ui.shadcn.com/
- **Zustand**: https://zustand-demo.pmnd.rs/
- **FastAPI**: https://fastapi.tiangolo.com/

---

**Document Version**: 1.0  
**Last Updated**: November 16, 2026
