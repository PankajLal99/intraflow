'use client'

import { useState, useCallback, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { 
  Save, Play, Settings, ArrowLeft, Plus, Trash2, 
  MessageSquare, GitBranch, Zap, Code 
} from 'lucide-react'
import axios from 'axios'

// Simple workflow builder (React Flow would be npm installed)
// This is a functional placeholder that works without React Flow

interface Node {
  id: string
  type: string
  data: any
  position?: { x: number; y: number }
}

function WorkflowBuilderContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const workflowId = searchParams?.get('id')

  const [workflow, setWorkflow] = useState({
    name: 'New Workflow',
    description: '',
    nodes: [] as Node[],
    edges: []
  })

  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [saving, setSaving] = useState(false)

  const nodeTypes = [
    { type: 'trigger', label: 'Trigger', icon: Zap, color: 'bg-green-100 text-green-600' },
    { type: 'message', label: 'Send Message', icon: MessageSquare, color: 'bg-blue-100 text-blue-600' },
    { type: 'condition', label: 'Condition', icon: GitBranch, color: 'bg-purple-100 text-purple-600' },
    { type: 'action', label: 'Action', icon: Code, color: 'bg-orange-100 text-orange-600' },
  ]

  const addNode = (type: string) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type,
      data: { label: `${type} node`, message: '', condition: '' },
      position: { x: 100, y: workflow.nodes.length * 100 + 100 }
    }
    setWorkflow({ ...workflow, nodes: [...workflow.nodes, newNode] })
  }

  const deleteNode = (nodeId: string) => {
    setWorkflow({
      ...workflow,
      nodes: workflow.nodes.filter(n => n.id !== nodeId)
    })
    if (selectedNode?.id === nodeId) {
      setSelectedNode(null)
    }
  }

  const updateNodeData = (nodeId: string, data: any) => {
    setWorkflow({
      ...workflow,
      nodes: workflow.nodes.map(n =>
        n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
      )
    })
  }

  const saveWorkflow = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('token')
      const definition = {
        nodes: workflow.nodes,
        edges: workflow.edges,
        variables: {}
      }

      if (workflowId) {
        await axios.put(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/workflows/${workflowId}`,
          { name: workflow.name, description: workflow.description, definition },
          { headers: { Authorization: `Bearer ${token}` } }
        )
      } else {
        await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/workflows`,
          { name: workflow.name, description: workflow.description, definition },
          { headers: { Authorization: `Bearer ${token}` } }
        )
      }
      
      alert('Workflow saved successfully!')
      router.push('/dashboard/workflows')
    } catch (error) {
      console.error('Failed to save workflow:', error)
      alert('Failed to save workflow')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <input
              type="text"
              value={workflow.name}
              onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
              className="text-xl font-semibold border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2"
            />
            <input
              type="text"
              value={workflow.description}
              onChange={(e) => setWorkflow({ ...workflow, description: e.target.value })}
              className="text-sm text-gray-600 border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 mt-1 block"
              placeholder="Add description..."
            />
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={saveWorkflow}
            disabled={saving}
            className="flex items-center bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Node Palette */}
        <div className="w-64 bg-white border-r p-4 overflow-y-auto">
          <h3 className="font-semibold text-gray-900 mb-4">Add Nodes</h3>
          <div className="space-y-2">
            {nodeTypes.map((nodeType) => (
              <button
                key={nodeType.type}
                onClick={() => addNode(nodeType.type)}
                className={`w-full flex items-center p-3 rounded-lg border hover:shadow transition ${nodeType.color}`}
              >
                <nodeType.icon className="h-5 w-5 mr-3" />
                <span className="font-medium">{nodeType.label}</span>
              </button>
            ))}
          </div>

          <div className="mt-8">
            <h3 className="font-semibold text-gray-900 mb-4">Workflow Info</h3>
            <div className="text-sm text-gray-600 space-y-2">
              <p>Nodes: {workflow.nodes.length}</p>
              <p>Status: Draft</p>
            </div>
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 bg-gray-50 p-6 overflow-auto">
          <div className="bg-white rounded-xl border p-6 min-h-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Workflow Canvas</h3>
            
            {workflow.nodes.length === 0 ? (
              <div className="text-center py-12">
                <Plus className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Add nodes from the left panel to build your workflow</p>
              </div>
            ) : (
              <div className="space-y-4">
                {workflow.nodes.map((node, index) => (
                  <div
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition ${
                      selectedNode?.id === node.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full ${
                          nodeTypes.find(t => t.type === node.type)?.color
                        } flex items-center justify-center mr-3`}>
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900 capitalize">{node.type}</p>
                          <p className="text-sm text-gray-600">{node.data.label}</p>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteNode(node.id)
                        }}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    {index < workflow.nodes.length - 1 && (
                      <div className="ml-4 mt-2 h-8 border-l-2 border-gray-300"></div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Properties Panel */}
        <div className="w-80 bg-white border-l p-4 overflow-y-auto">
          <h3 className="font-semibold text-gray-900 mb-4">Properties</h3>
          
          {selectedNode ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Node Type
                </label>
                <input
                  type="text"
                  value={selectedNode.type}
                  disabled
                  className="w-full px-3 py-2 border rounded-lg bg-gray-100 capitalize"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Label
                </label>
                <input
                  type="text"
                  value={selectedNode.data.label}
                  onChange={(e) => updateNodeData(selectedNode.id, { label: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {selectedNode.type === 'message' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message Text
                  </label>
                  <textarea
                    value={selectedNode.data.message || ''}
                    onChange={(e) => updateNodeData(selectedNode.id, { message: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    placeholder="Enter message text..."
                  />
                </div>
              )}

              {selectedNode.type === 'condition' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Condition
                  </label>
                  <textarea
                    value={selectedNode.data.condition || ''}
                    onChange={(e) => updateNodeData(selectedNode.id, { condition: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="e.g., message contains 'order'"
                  />
                </div>
              )}

              <button
                onClick={() => deleteNode(selectedNode.id)}
                className="w-full flex items-center justify-center px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Node
              </button>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Settings className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <p>Select a node to edit its properties</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function WorkflowBuilderPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <WorkflowBuilderContent />
    </Suspense>
  )
}
