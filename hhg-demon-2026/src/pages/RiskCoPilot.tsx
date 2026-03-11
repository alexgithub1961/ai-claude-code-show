import { useState, useEffect } from 'react'
import { AlertTriangle, TrendingDown, Users, FileText, CheckCircle2 } from 'lucide-react'
import { Order } from '../types'
import { useStore } from '../store'

export default function RiskCoPilot() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  
  const {
    selectedOrder,
    currentRiskAssessment,
    currentRFQDraft,
    setSelectedOrder,
    setRiskAssessment,
    setRFQDraft
  } = useStore()

  useEffect(() => {
    fetch('/data/orders.json').then(r => r.json()).then(setOrders)
  }, [])

  const handleSelectOrder = async (orderId: string) => {
    setLoading(true)
    setSelectedOrder(orderId)
    
    // Simulate AI analysis delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Load risk assessment
    const assessment = await fetch('/data/risk-assessment.json').then(r => r.json())
    setRiskAssessment(assessment)
    
    setLoading(false)
  }

  const handleGenerateRFQ = async () => {
    setLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const rfq = await fetch('/data/rfq-draft.json').then(r => r.json())
    setRFQDraft(rfq)
    
    setLoading(false)
  }

  const selectedOrderData = orders.find(o => o.orderId === selectedOrder)
  const riskLevelColors = {
    low: 'bg-green-100 text-green-800 border-green-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-red-100 text-red-800 border-red-200'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Order Execution & Risk Co-Pilot</h2>
        <p className="text-gray-600">
          <strong>Risk surfaced before orders become expensive.</strong> AI analyzes overstock patterns,
          event delivery viability, and supplier fit to recommend optimal procurement actions.
        </p>
      </div>

      {/* Order Queue */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Incoming Orders for Review</h3>
        <div className="space-y-3">
          {orders.map(order => (
            <button
              key={order.orderId}
              onClick={() => handleSelectOrder(order.orderId)}
              disabled={loading}
              className={`
                w-full text-left p-4 rounded-lg border-2 transition
                ${selectedOrder === order.orderId
                  ? 'border-hhg-primary bg-blue-50'
                  : order.orderId === 'ORD-2026-043'
                    ? 'border-red-300 bg-red-50 hover:border-red-400'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="font-semibold text-gray-900">{order.campaign}</h4>
                    {order.orderId === 'ORD-2026-043' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        High Risk
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>{order.client}</span>
                    <span>•</span>
                    <span>Event: {new Date(order.eventDate).toLocaleDateString()}</span>
                    <span>•</span>
                    <span className="font-medium">${order.totalValue.toLocaleString()}</span>
                  </div>
                </div>
                {selectedOrder === order.orderId && (
                  <CheckCircle2 className="w-5 h-5 text-hhg-primary" />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* AI Analysis Loading */}
      {loading && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hhg-primary mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">AI is analyzing order risks and supplier fit...</p>
        </div>
      )}

      {/* Risk Assessment Results */}
      {!loading && currentRiskAssessment && selectedOrderData && (
        <div className="space-y-6">
          {/* Overall Risk Summary */}
          <div className={`rounded-lg border-2 p-6 ${riskLevelColors[currentRiskAssessment.overallRiskLevel]}`}>
            <div className="flex items-start space-x-4">
              <AlertTriangle className="w-8 h-8 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-lg font-bold mb-2">
                  Overall Risk Level: {currentRiskAssessment.overallRiskLevel.toUpperCase()}
                </h3>
                <p className="opacity-90">
                  {currentRiskAssessment.risks.length} risks identified across overstock, deadlines, and supplier fit.
                  AI recommends immediate action on {currentRiskAssessment.recommendations.length} items.
                </p>
              </div>
            </div>
          </div>

          {/* Risk Cards */}
          <div className="grid grid-cols-2 gap-4">
            {currentRiskAssessment.risks.map((risk, idx) => (
              <div key={idx} className="bg-white rounded-lg shadow-md p-5 border-l-4" style={{
                borderLeftColor: risk.severity === 'critical' ? '#dc2626' : 
                                 risk.severity === 'high' ? '#ea580c' :
                                 risk.severity === 'medium' ? '#ca8a04' : '#16a34a'
              }}>
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{risk.title}</h4>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    risk.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    risk.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                    risk.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {risk.severity}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{risk.description}</p>
                <div className="bg-gray-50 rounded p-2 text-xs text-gray-700">
                  <strong>Impact:</strong> {risk.impact}
                </div>
              </div>
            ))}
          </div>

          {/* AI Recommendations */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingDown className="w-5 h-5 mr-2 text-green-600" />
              AI-Powered Recommendations
            </h3>
            <div className="space-y-4">
              {currentRiskAssessment.recommendations.map((rec, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">{rec.title}</h4>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {rec.type.replace('-', ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                  <div className="bg-green-50 rounded p-3 mb-3">
                    <p className="text-sm text-green-800">
                      <strong>Expected Impact:</strong> {rec.expectedImpact}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-gray-700 mb-2">Action Items:</p>
                    <ul className="space-y-1">
                      {rec.actionItems.map((action, aidx) => (
                        <li key={aidx} className="text-xs text-gray-600 flex items-start">
                          <span className="text-hhg-primary mr-2">•</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Supplier Analysis */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-blue-600" />
              Supplier Performance Analysis
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Supplier</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">On-Time %</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quality</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Overall</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recommended</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {currentRiskAssessment.supplierAnalysis.map((supplier, idx) => (
                    <tr key={idx} className={supplier.recommendedForItems.length > 0 ? 'bg-green-50' : ''}>
                      <td className="px-4 py-3 text-sm">
                        <div className="font-medium text-gray-900">{supplier.supplierName}</div>
                        <div className="text-gray-500">{supplier.supplierCode}</div>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`font-semibold ${
                          supplier.onTimeRate >= 90 ? 'text-green-600' :
                          supplier.onTimeRate >= 80 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {supplier.onTimeRate}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm font-medium">{supplier.qualityScore.toFixed(1)}/5.0</td>
                      <td className="px-4 py-3 text-sm font-medium">{supplier.priceCompetitiveness.toFixed(1)}/5.0</td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`font-semibold ${
                          supplier.overallScore >= 4.2 ? 'text-green-600' :
                          supplier.overallScore >= 3.8 ? 'text-yellow-600' : 'text-orange-600'
                        }`}>
                          {supplier.overallScore.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {supplier.recommendedForItems.length > 0 ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            ✓ Recommended
                          </span>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* RFQ Generation */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-purple-600" />
                  RFQ Draft Generation
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  AI can draft an RFQ for recommended supplier switches
                </p>
              </div>
              {!currentRFQDraft && (
                <button
                  onClick={handleGenerateRFQ}
                  disabled={loading}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-purple-700 transition disabled:opacity-50"
                >
                  Generate RFQ Draft
                </button>
              )}
            </div>

            {currentRFQDraft && (
              <div className="border-2 border-purple-200 rounded-lg p-4 bg-purple-50">
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">RFQ {currentRFQDraft.rfqId}</h4>
                    <span className="text-sm text-gray-600">Deadline: {new Date(currentRFQDraft.deadline).toLocaleDateString()}</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Suppliers: {currentRFQDraft.suppliers.join(', ')}
                  </p>
                </div>

                <div className="bg-white rounded p-4 mb-3">
                  <h5 className="font-semibold text-sm text-gray-900 mb-2">Special Requirements:</h5>
                  <ul className="space-y-1">
                    {currentRFQDraft.specialRequirements.map((req, idx) => (
                      <li key={idx} className="text-xs text-gray-700 flex items-start">
                        <span className="text-purple-600 mr-2">•</span>
                        <span>{req}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="space-y-2">
                  {currentRFQDraft.items.map((item, idx) => (
                    <div key={idx} className="bg-white rounded p-3 text-sm">
                      <div className="font-semibold text-gray-900 mb-1">{item.itemName}</div>
                      <div className="text-gray-600">
                        Quantity: {item.quantity} • Required by: {new Date(item.requiredBy).toLocaleDateString()}
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        {item.specifications.slice(0, 2).join(' • ')}
                      </div>
                    </div>
                  ))}
                </div>

                <button className="w-full mt-4 bg-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-purple-700 transition">
                  Export RFQ Document
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
