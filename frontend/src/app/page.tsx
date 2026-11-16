'use client'

import Link from 'next/link'
import { ArrowRight, MessageCircle, Workflow, Shield, Zap, Users, TrendingUp } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <MessageCircle className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">IntraFlow</span>
            </div>
            <div className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600">Features</a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600">Pricing</a>
              <a href="#docs" className="text-gray-700 hover:text-blue-600">Docs</a>
            </div>
            <div className="flex space-x-4">
              <Link href="/login" className="text-gray-700 hover:text-blue-600">
                Login
              </Link>
              <Link 
                href="/signup" 
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Automate Your WhatsApp
            <br />
            <span className="text-blue-600">with AI-Powered Agents</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Build intelligent WhatsApp workflows without code. Handle customer inquiries, 
            process orders, and provide 24/7 support with AI agents.
          </p>
          <div className="flex justify-center space-x-4">
            <Link 
              href="/signup" 
              className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 flex items-center"
            >
              Get Started Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link 
              href="#demo" 
              className="border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-50"
            >
              Watch Demo
            </Link>
          </div>
        </div>
      </div>

      {/* Features */}
      <div id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Automate WhatsApp
            </h2>
            <p className="text-xl text-gray-600">
              Built for businesses that want to scale customer interactions
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 border rounded-xl hover:shadow-lg transition">
              <Workflow className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Visual Workflow Builder</h3>
              <p className="text-gray-600">
                Create complex conversation flows with drag-and-drop. No coding required.
              </p>
            </div>

            <div className="p-6 border rounded-xl hover:shadow-lg transition">
              <Shield className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">AI Guardrails</h3>
              <p className="text-gray-600">
                Parent Agent ensures safety, content filtering, and context boundaries.
              </p>
            </div>

            <div className="p-6 border rounded-xl hover:shadow-lg transition">
              <Zap className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
              <p className="text-gray-600">
                Process thousands of messages per minute with async processing.
              </p>
            </div>

            <div className="p-6 border rounded-xl hover:shadow-lg transition">
              <Users className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Multi-Tenant</h3>
              <p className="text-gray-600">
                Serve multiple clients with complete data isolation and security.
              </p>
            </div>

            <div className="p-6 border rounded-xl hover:shadow-lg transition">
              <TrendingUp className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Analytics</h3>
              <p className="text-gray-600">
                Track performance, user satisfaction, and agent effectiveness.
              </p>
            </div>

            <div className="p-6 border rounded-xl hover:shadow-lg transition">
              <MessageCircle className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Multi-Provider LLM</h3>
              <p className="text-gray-600">
                Support for OpenAI, Claude, and Gemini. Choose what works for you.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing */}
      <div id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Start free, scale as you grow
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-xl border">
              <h3 className="text-2xl font-bold mb-2">Starter</h3>
              <div className="text-4xl font-bold text-blue-600 mb-4">
                $29<span className="text-lg text-gray-600">/mo</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-500 mr-2" />
                  1 WhatsApp number
                </li>
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-500 mr-2" />
                  10 workflows
                </li>
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-500 mr-2" />
                  1,000 messages/month
                </li>
              </ul>
              <Link 
                href="/signup" 
                className="block w-full text-center bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700"
              >
                Get Started
              </Link>
            </div>

            <div className="bg-blue-600 text-white p-8 rounded-xl border-4 border-blue-700 relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-gray-900 px-4 py-1 rounded-full text-sm font-semibold">
                Most Popular
              </div>
              <h3 className="text-2xl font-bold mb-2">Business</h3>
              <div className="text-4xl font-bold mb-4">
                $99<span className="text-lg opacity-80">/mo</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-300 mr-2" />
                  2 WhatsApp numbers
                </li>
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-300 mr-2" />
                  50 workflows
                </li>
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-300 mr-2" />
                  10,000 messages/month
                </li>
              </ul>
              <Link 
                href="/signup" 
                className="block w-full text-center bg-white text-blue-600 px-4 py-3 rounded-lg hover:bg-gray-100 font-semibold"
              >
                Get Started
              </Link>
            </div>

            <div className="bg-white p-8 rounded-xl border">
              <h3 className="text-2xl font-bold mb-2">Enterprise</h3>
              <div className="text-4xl font-bold text-blue-600 mb-4">
                $299<span className="text-lg text-gray-600">/mo</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-500 mr-2" />
                  5 WhatsApp numbers
                </li>
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-500 mr-2" />
                  Unlimited workflows
                </li>
                <li className="flex items-center">
                  <ArrowRight className="h-5 w-5 text-green-500 mr-2" />
                  100,000 messages/month
                </li>
              </ul>
              <Link 
                href="/signup" 
                className="block w-full text-center bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="py-20 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Automate Your WhatsApp?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join hundreds of businesses using IntraFlow to handle customer interactions at scale
          </p>
          <Link 
            href="/signup" 
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100"
          >
            Start Your Free Trial
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <MessageCircle className="h-6 w-6" />
                <span className="ml-2 text-xl font-bold">IntraFlow</span>
              </div>
              <p className="text-gray-400">
                Automate Your Internal Communications with AI
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#docs">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#about">About</a></li>
                <li><a href="#blog">Blog</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#privacy">Privacy</a></li>
                <li><a href="#terms">Terms</a></li>
                <li><a href="#security">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2026 IntraFlow. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
