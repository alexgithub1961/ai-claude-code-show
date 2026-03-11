import { ArrowRight, Clock, TrendingDown, Target, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Overview() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-hhg-primary to-blue-700 rounded-lg shadow-lg p-8 text-white">
        <h2 className="text-3xl font-bold mb-4">
          AI-Powered Intelligence for Marketing Supply Chain Excellence
        </h2>
        <p className="text-lg opacity-90 mb-6 max-w-3xl">
          Transform operational friction into competitive advantage with embedded AI co-pilots
          that surface insights, reduce risk, and accelerate decision-making across the demand-to-delivery lifecycle.
        </p>
        <div className="flex items-center space-x-4">
          <Link
            to="/buy-window"
            className="bg-white text-hhg-primary px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition inline-flex items-center space-x-2"
          >
            <span>Explore Buy Window Co-Pilot</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/risk-copilot"
            className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-hhg-primary transition inline-flex items-center space-x-2"
          >
            <span>Explore Risk Co-Pilot</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>

      {/* Lifecycle Diagram */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Supply Chain Lifecycle Focus</h3>
        <div className="flex items-center justify-between mb-8">
          {['Demand Aggregation', 'Procurement Allocation', 'Production & Drawdown', 'Event Readiness'].map((stage, idx) => (
            <div key={stage} className="flex items-center">
              <div className="text-center">
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-hhg-primary to-blue-600 flex items-center justify-center mb-3">
                  <span className="text-white font-bold text-lg">{idx + 1}</span>
                </div>
                <p className="text-sm font-medium text-gray-700">{stage}</p>
              </div>
              {idx < 3 && (
                <ArrowRight className="w-8 h-8 text-gray-400 mx-4" />
              )}
            </div>
          ))}
        </div>
        <p className="text-gray-600 text-center max-w-4xl mx-auto">
          Our AI co-pilots embed intelligence at critical decision points where supply-chain friction,
          missed deadlines, and margin leakage typically occur.
        </p>
      </div>

      {/* Pain Points */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Operational Challenges We Address</h3>
        <div className="grid grid-cols-2 gap-6">
          {[
            {
              title: 'Manual Order Reconstruction',
              problem: 'Repeat buyers spend hours recreating seasonal orders when catalog item IDs roll over',
              impact: 'Delayed orders, missed buy windows, manual errors'
            },
            {
              title: 'Fragmented Risk Visibility',
              problem: 'Procurement decisions rely on subjective supplier judgments and disconnected data',
              impact: 'Overstock waste, deadline misses, suboptimal supplier selection'
            },
            {
              title: 'Event Delivery Risk',
              problem: 'Critical campaign deadlines threatened by supplier lead time variability',
              impact: 'Last-minute expedite costs, reputation damage, client dissatisfaction'
            },
            {
              title: 'Dead Stock Exposure',
              problem: 'Forecasted demand disconnects from actual call-off patterns',
              impact: 'Margin leakage, wasted working capital, inventory carrying costs'
            }
          ].map((pain) => (
            <div key={pain.title} className="border border-gray-200 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-2">{pain.title}</h4>
              <p className="text-sm text-gray-600 mb-3">{pain.problem}</p>
              <p className="text-xs text-hhg-secondary font-medium">
                Impact: {pain.impact}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Interventions */}
      <div className="grid grid-cols-2 gap-6">
        <Link to="/buy-window" className="block group">
          <div className="bg-white rounded-lg shadow-md p-8 hover:shadow-xl transition">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Clock className="w-6 h-6 text-hhg-primary" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Buy Window Co-Pilot</h3>
            <p className="text-gray-600 mb-4">
              Auto-reconstruct recurring campaign orders with intelligent item mapping.
              <strong> Seconds, not hours</strong> to rebuild seasonal purchases.
            </p>
            <div className="flex items-center text-hhg-primary font-semibold group-hover:translate-x-2 transition-transform">
              <span>Explore Co-Pilot</span>
              <ArrowRight className="w-5 h-5 ml-2" />
            </div>
          </div>
        </Link>

        <Link to="/risk-copilot" className="block group">
          <div className="bg-white rounded-lg shadow-md p-8 hover:shadow-xl transition">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
              <Target className="w-6 h-6 text-hhg-secondary" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Order Execution & Risk Co-Pilot</h3>
            <p className="text-gray-600 mb-4">
              Surface overstock and deadline risks before orders become expensive.
              <strong> AI embedded in workflow</strong>, not bolted on.
            </p>
            <div className="flex items-center text-hhg-primary font-semibold group-hover:translate-x-2 transition-transform">
              <span>Explore Co-Pilot</span>
              <ArrowRight className="w-5 h-5 ml-2" />
            </div>
          </div>
        </Link>
      </div>

      {/* Impact Cards */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Expected Business Impact</h3>
        <div className="grid grid-cols-4 gap-6">
          {[
            { icon: Zap, label: 'Order Rebuild Time', value: '90% faster', color: 'bg-yellow-100 text-yellow-700' },
            { icon: TrendingDown, label: 'Dead Stock Risk', value: '30-40% reduction', color: 'bg-green-100 text-green-700' },
            { icon: Target, label: 'Event SLA Performance', value: '25% improvement', color: 'bg-blue-100 text-blue-700' },
            { icon: Clock, label: 'Time to Pilot', value: '4-6 weeks', color: 'bg-purple-100 text-purple-700' }
          ].map((metric) => (
            <div key={metric.label} className="text-center">
              <div className={`w-16 h-16 rounded-full ${metric.color} flex items-center justify-center mx-auto mb-3`}>
                <metric.icon className="w-8 h-8" />
              </div>
              <p className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</p>
              <p className="text-sm text-gray-600">{metric.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gray-100 rounded-lg p-8 text-center">
        <h3 className="text-xl font-bold text-gray-900 mb-3">
          Ready to Transform Your Supply Chain Workflows?
        </h3>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          These demos represent tangible proof of understanding and credible starting points for a real pilot engagement.
          Let's discuss how to bring this intelligence into your operations.
        </p>
        <div className="flex items-center justify-center space-x-4">
          <Link
            to="/architecture"
            className="bg-hhg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            View Technical Architecture
          </Link>
          <Link
            to="/data-story"
            className="border-2 border-hhg-primary text-hhg-primary px-6 py-3 rounded-lg font-semibold hover:bg-hhg-primary hover:text-white transition"
          >
            Understand the Data
          </Link>
        </div>
      </div>
    </div>
  )
}
