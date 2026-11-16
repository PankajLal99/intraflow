'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  MessageCircle, Home, Workflow, BarChart3, Settings, 
  Users, MessageSquare, LogOut, Menu, X 
} from 'lucide-react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [tenant, setTenant] = useState<any>(null)

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }

    // Load user and tenant data
    const userData = localStorage.getItem('user')
    const tenantData = localStorage.getItem('tenant')
    
    if (userData) setUser(JSON.parse(userData))
    if (tenantData) setTenant(JSON.parse(tenantData))
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('tenant')
    router.push('/login')
  }

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Workflows', href: '/dashboard/workflows', icon: Workflow },
    { name: 'Conversations', href: '/dashboard/conversations', icon: MessageSquare },
    { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
    { name: 'Team', href: '/dashboard/team', icon: Users },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r transform transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b">
            <Link href="/dashboard" className="flex items-center">
              <MessageCircle className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold">IntraFlow</span>
            </Link>
            <button onClick={() => setSidebarOpen(false)} className="lg:hidden">
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Tenant Info */}
          <div className="px-6 py-4 border-b bg-blue-50">
            <p className="text-sm text-gray-600">Workspace</p>
            <p className="font-semibold text-gray-900">{tenant?.name || 'Loading...'}</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition"
              >
                <item.icon className="h-5 w-5 mr-3" />
                {item.name}
              </Link>
            ))}
          </nav>

          {/* User Profile */}
          <div className="border-t p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                  {user?.full_name?.[0] || 'U'}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-red-600 transition"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <div className="sticky top-0 z-40 h-16 bg-white border-b flex items-center px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden mr-4"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex-1" />
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {tenant?.plan} Plan
            </span>
          </div>
        </div>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}
