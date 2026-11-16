'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Plus, Play, Edit, Trash2, Copy } from 'lucide-react'
import axios from 'axios'

interface Workflow {
  id: string
  name: string
  description: string
  status: string
  version: number
  updated_at: string
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWorkflows()
  }, [])

  const loadWorkflows = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/workflows`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
      setWorkflows(response.data)
    } catch (error) {
      console.error('Failed to load workflows:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteWorkflow = async (id: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return

    try {
      const token = localStorage.getItem('token')
      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/workflows/${id}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
      loadWorkflows()
    } catch (error) {
      console.error('Failed to delete workflow:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
          <p className="text-gray-600 mt-1">Create and manage your WhatsApp automation workflows</p>
        </div>
        <Link
          href="/dashboard/workflows/builder"
          className="flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Workflow
        </Link>
      </div>

      {/* Workflows Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading workflows...</p>
        </div>
      ) : workflows.length === 0 ? (
        <div className="bg-white rounded-xl border p-12 text-center">
          <div className="max-w-md mx-auto">
            <Play className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No workflows yet</h3>
            <p className="text-gray-600 mb-6">
              Create your first workflow to start automating WhatsApp conversations
            </p>
            <Link
              href="/dashboard/workflows/builder"
              className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
            >
              <Plus className="h-5 w-5 mr-2" />
              Create Your First Workflow
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <div key={workflow.id} className="bg-white rounded-xl border hover:shadow-lg transition">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{workflow.name}</h3>
                    <p className="text-sm text-gray-600">{workflow.description || 'No description'}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    workflow.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : workflow.status === 'draft'
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {workflow.status}
                  </span>
                </div>

                <div className="flex items-center text-sm text-gray-500 mb-4">
                  <span>Version {workflow.version}</span>
                  <span className="mx-2">•</span>
                  <span>Updated {new Date(workflow.updated_at).toLocaleDateString()}</span>
                </div>

                <div className="flex space-x-2">
                  <Link
                    href={`/dashboard/workflows/builder?id=${workflow.id}`}
                    className="flex-1 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </Link>
                  <button
                    onClick={() => deleteWorkflow(workflow.id)}
                    className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Start Templates */}
      <div className="bg-blue-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Start Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-semibold text-gray-900 mb-2">Customer Support Bot</h4>
            <p className="text-sm text-gray-600 mb-3">Handle common inquiries and route to support team</p>
            <button className="text-blue-600 text-sm font-semibold hover:text-blue-700">
              Use Template →
            </button>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-semibold text-gray-900 mb-2">Order Tracking</h4>
            <p className="text-sm text-gray-600 mb-3">Let customers check their order status automatically</p>
            <button className="text-blue-600 text-sm font-semibold hover:text-blue-700">
              Use Template →
            </button>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-semibold text-gray-900 mb-2">Lead Qualification</h4>
            <p className="text-sm text-gray-600 mb-3">Qualify leads and schedule appointments</p>
            <button className="text-blue-600 text-sm font-semibold hover:text-blue-700">
              Use Template →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
