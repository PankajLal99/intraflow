'use client'

import { useState, useEffect } from 'react'
import { 
  MessageCircle, TrendingUp, Users, Workflow, 
  ArrowUp, ArrowDown, Activity 
} from 'lucide-react'
import axios from 'axios'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalMessages: 1247,
    activeWorkflows: 5,
    conversations: 89,
    responseTime: '1.2s'
  })

  const [recentActivity, setRecentActivity] = useState([
    { id: 1, user: '+1234567890', message: 'Order tracking inquiry', time: '2 min ago', status: 'completed' },
    { id: 2, user: '+1987654321', message: 'Product search', time: '5 min ago', status: 'completed' },
    { id: 3, user: '+1555123456', message: 'Customer support', time: '8 min ago', status: 'in_progress' },
  ])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back! Here's what's happening.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl border">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <MessageCircle className="h-6 w-6 text-blue-600" />
            </div>
            <span className="flex items-center text-green-600 text-sm font-semibold">
              <ArrowUp className="h-4 w-4 mr-1" />
              12%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.totalMessages}</p>
          <p className="text-sm text-gray-600 mt-1">Total Messages</p>
        </div>

        <div className="bg-white p-6 rounded-xl border">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <Workflow className="h-6 w-6 text-green-600" />
            </div>
            <span className="flex items-center text-green-600 text-sm font-semibold">
              <ArrowUp className="h-4 w-4 mr-1" />
              5%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.activeWorkflows}</p>
          <p className="text-sm text-gray-600 mt-1">Active Workflows</p>
        </div>

        <div className="bg-white p-6 rounded-xl border">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
            <span className="flex items-center text-green-600 text-sm font-semibold">
              <ArrowUp className="h-4 w-4 mr-1" />
              8%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.conversations}</p>
          <p className="text-sm text-gray-600 mt-1">Conversations</p>
        </div>

        <div className="bg-white p-6 rounded-xl border">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <Activity className="h-6 w-6 text-orange-600" />
            </div>
            <span className="flex items-center text-green-600 text-sm font-semibold">
              <ArrowDown className="h-4 w-4 mr-1" />
              15%
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats.responseTime}</p>
          <p className="text-sm text-gray-600 mt-1">Avg Response Time</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Messages Chart */}
        <div className="bg-white p-6 rounded-xl border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Message Volume</h3>
          <div className="h-64 flex items-end justify-between space-x-2">
            {[40, 65, 45, 80, 55, 70, 90].map((height, i) => (
              <div
                key={i}
                className="flex-1 bg-blue-500 rounded-t-lg hover:bg-blue-600 transition cursor-pointer"
                style={{ height: `${height}%` }}
                title={`Day ${i + 1}`}
              />
            ))}
          </div>
          <div className="flex justify-between mt-4 text-sm text-gray-600">
            <span>Mon</span>
            <span>Tue</span>
            <span>Wed</span>
            <span>Thu</span>
            <span>Fri</span>
            <span>Sat</span>
            <span>Sun</span>
          </div>
        </div>

        {/* Agent Performance */}
        <div className="bg-white p-6 rounded-xl border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Performance</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Product Search</span>
                <span className="font-semibold">85%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Order Management</span>
                <span className="font-semibold">92%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '92%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Customer Support</span>
                <span className="font-semibold">78%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '78%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        </div>
        <div className="divide-y">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition">
              <div className="flex items-center">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <MessageCircle className="h-5 w-5 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="font-medium text-gray-900">{activity.user}</p>
                  <p className="text-sm text-gray-600">{activity.message}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">{activity.time}</p>
                <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${
                  activity.status === 'completed' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {activity.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
