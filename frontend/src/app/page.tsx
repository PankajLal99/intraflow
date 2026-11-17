'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  MessageSquare, Zap, Shield, BarChart3, Bot, 
  Workflow, Clock, CheckCircle2, ArrowRight, Star,
  Users, Globe, Lock, TrendingUp, Menu, X
} from 'lucide-react'

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const features = [
    {
      icon: Bot,
      title: 'AI-Powered Agents',
      description: 'Intelligent agents that understand context and handle complex conversations with LangChain integration.',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Workflow,
      title: 'Visual Workflow Builder',
      description: 'Drag-and-drop interface to create sophisticated automation workflows without coding.',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: Shield,
      title: 'Parent Agent Guardrails',
      description: '5-stage safety system ensures compliance and protects your brand reputation.',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: BarChart3,
      title: 'Real-time Analytics',
      description: 'Track performance, engagement, and ROI with comprehensive dashboards.',
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: Users,
      title: 'Multi-Tenant Architecture',
      description: 'Enterprise-grade isolation with dedicated resources for each organization.',
      color: 'from-indigo-500 to-blue-500'
    },
    {
      icon: Zap,
      title: 'Instant Deployment',
      description: 'Go live in minutes with our pre-configured templates and integrations.',
      color: 'from-yellow-500 to-orange-500'
    }
  ]

  const stats = [
    { label: 'Messages Processed', value: '10M+', icon: MessageSquare },
    { label: 'Automation Rate', value: '95%', icon: Bot },
    { label: 'Response Time', value: '<2s', icon: Clock },
    { label: 'Customer Satisfaction', value: '4.9/5', icon: Star }
  ]

  const pricing = [
    {
      name: 'Starter',
      price: '$49',
      period: '/month',
      description: 'Perfect for small businesses',
      features: [
        '5,000 messages/month',
        '2 workflows',
        'Basic AI agents',
        'Email support',
        'Standard integrations'
      ],
      cta: 'Start Free Trial',
      popular: false
    },
    {
      name: 'Professional',
      price: '$199',
      period: '/month',
      description: 'For growing companies',
      features: [
        '50,000 messages/month',
        'Unlimited workflows',
        'Advanced AI agents',
        'Priority support',
        'Custom integrations',
        'Analytics dashboard',
        'Multi-language support'
      ],
      cta: 'Get Started',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For large organizations',
      features: [
        'Unlimited messages',
        'Unlimited workflows',
        'Custom AI training',
        'Dedicated support',
        'SLA guarantee',
        'Advanced security',
        'White-label option',
        'API access'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled ? 'bg-white/95 backdrop-blur-md shadow-lg' : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                IntraFlow
              </span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition">Features</a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600 transition">Pricing</a>
              <a href="#about" className="text-gray-700 hover:text-blue-600 transition">About</a>
              <Link href="/login" className="text-gray-700 hover:text-blue-600 transition">
                Login
              </Link>
              <Link 
                href="/signup" 
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg hover:shadow-lg transition-all transform hover:scale-105"
              >
                Get Started Free
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-4 py-4 space-y-3">
              <a href="#features" className="block text-gray-700 hover:text-blue-600">Features</a>
              <a href="#pricing" className="block text-gray-700 hover:text-blue-600">Pricing</a>
              <a href="#about" className="block text-gray-700 hover:text-blue-600">About</a>
              <Link href="/login" className="block text-gray-700 hover:text-blue-600">Login</Link>
              <Link href="/signup" className="block bg-blue-600 text-white px-4 py-2 rounded-lg text-center">
                Get Started Free
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-block mb-4">
            <span className="bg-blue-100 text-blue-600 px-4 py-2 rounded-full text-sm font-semibold">
              🚀 Now with AI-Powered Automation
            </span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Automate Your
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"> WhatsApp </span>
            Conversations
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Build intelligent chatbots with visual workflows, AI agents, and enterprise-grade security. 
            No coding required.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link 
              href="/signup"
              className="group bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl hover:shadow-2xl transition-all transform hover:scale-105 flex items-center justify-center space-x-2"
            >
              <span className="font-semibold">Start Free Trial</span>
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <button className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-xl hover:border-blue-600 hover:text-blue-600 transition-all">
              Watch Demo
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <stat.icon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-600">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Business
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to create, deploy, and manage intelligent WhatsApp automation
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="group bg-gradient-to-br from-white to-gray-50 p-8 rounded-2xl border border-gray-200 hover:border-transparent hover:shadow-2xl transition-all transform hover:-translate-y-2"
              >
                <div className={`bg-gradient-to-r ${feature.color} p-3 rounded-xl w-fit mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Get Started in 3 Simple Steps
            </h2>
            <p className="text-xl text-gray-600">
              From setup to automation in minutes
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Connect Your WhatsApp',
                description: 'Scan QR code to connect your WhatsApp Business account securely',
                icon: MessageSquare
              },
              {
                step: '02',
                title: 'Build Your Workflow',
                description: 'Use our visual builder to create automation workflows with drag-and-drop',
                icon: Workflow
              },
              {
                step: '03',
                title: 'Go Live & Scale',
                description: 'Deploy instantly and let AI handle conversations while you focus on growth',
                icon: TrendingUp
              }
            ].map((step, index) => (
              <div key={index} className="relative">
                <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
                  <div className="absolute -top-4 -left-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg">
                    {step.step}
                  </div>
                  <step.icon className="h-12 w-12 text-blue-600 mb-4" />
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">{step.title}</h3>
                  <p className="text-gray-600">{step.description}</p>
                </div>
                {index < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ArrowRight className="h-8 w-8 text-blue-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that fits your business needs
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {pricing.map((plan, index) => (
              <div 
                key={index}
                className={`relative bg-white rounded-2xl p-8 transition-all transform hover:scale-105 ${
                  plan.popular 
                    ? 'border-2 border-blue-600 shadow-2xl' 
                    : 'border border-gray-200 hover:border-blue-300'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                  <div className="flex items-baseline justify-center">
                    <span className="text-5xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600 ml-2">{plan.period}</span>
                  </div>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, fIndex) => (
                    <li key={fIndex} className="flex items-center">
                      <CheckCircle2 className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href="/signup"
                  className={`block text-center py-3 rounded-xl font-semibold transition-all ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg transform hover:scale-105'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your WhatsApp Communication?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of businesses automating customer conversations with IntraFlow
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold hover:shadow-2xl transition-all transform hover:scale-105"
            >
              Start Free 14-Day Trial
            </Link>
            <button className="border-2 border-white text-white px-8 py-4 rounded-xl hover:bg-white hover:text-blue-600 transition-all">
              Schedule Demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <MessageSquare className="h-6 w-6" />
                <span className="text-xl font-bold">IntraFlow</span>
              </div>
              <p className="text-gray-400">
                AI-powered WhatsApp automation for modern businesses
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition">Features</a></li>
                <li><a href="#" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                <li><a href="#" className="hover:text-white transition">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2026 IntraFlow. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
