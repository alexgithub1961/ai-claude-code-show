import { useState, useEffect } from 'react'
import { Clock, CheckCircle, ArrowRight } from 'lucide-react'
import { PreviousOrder, CatalogItem, CartItem } from '../types'
import { useStore } from '../store'

export default function BuyWindow() {
  const [previousOrders, setPreviousOrders] = useState<PreviousOrder[]>([])
  const [catalog, setCatalog] = useState<CatalogItem[]>([])
  const [loading, setLoading] = useState(false)
  
  const { 
    selectedPreviousOrder,
    cart,
    setSelectedPreviousOrder,
    setCart,
    updateCartItem
  } = useStore()

  useEffect(() => {
    // Load data
    Promise.all([
      fetch('/data/previous-orders.json').then(r => r.json()),
      fetch('/data/catalog.json').then(r => r.json())
    ]).then(([orders, cat]) => {
      setPreviousOrders(orders)
      setCatalog(cat)
    })
  }, [])

  const handleSelectOrder = async (orderId: string) => {
    setLoading(true)
    setSelectedPreviousOrder(orderId)
    
    // Simulate AI mapping delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const order = previousOrders.find(o => o.orderId === orderId)
    if (!order) return

    // AI-powered mapping from legacy items to current catalog
    const mappedCart: CartItem[] = order.items.map(item => {
      // Deterministic mapping based on category
      const matchedItem = catalog.find(c => 
        c.category === item.category && c.available
      ) || catalog[0]

      return {
        catalogItem: matchedItem,
        suggestedQuantity: item.quantity,
        mappedFrom: item,
        matchConfidence: item.category === matchedItem.category ? 95 : 75,
        userAdjusted: false
      }
    })

    setCart(mappedCart)
    setLoading(false)
  }

  const selectedOrder = previousOrders.find(o => o.orderId === selectedPreviousOrder)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Smart Buy Window Co-Pilot</h2>
            <p className="text-gray-600">
              Reconstruct recurring seasonal orders in <strong>seconds, not hours</strong>. 
              AI maps legacy item IDs to current catalog with confidence scoring.
            </p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 text-center min-w-[200px]">
            <Clock className="w-6 h-6 text-hhg-primary mx-auto mb-2" />
            <div className="text-sm text-gray-600 mb-1">Buy Window Closes</div>
            <div className="text-2xl font-bold text-gray-900">14 Days</div>
            <div className="text-xs text-gray-500">March 25, 2026</div>
          </div>
        </div>
      </div>

      {/* Previous Orders Selection */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Previous Order to Reconstruct</h3>
        <div className="grid grid-cols-2 gap-4">
          {previousOrders.map(order => (
            <button
              key={order.orderId}
              onClick={() => handleSelectOrder(order.orderId)}
              disabled={loading}
              className={`
                text-left p-4 rounded-lg border-2 transition
                ${selectedPreviousOrder === order.orderId
                  ? 'border-hhg-primary bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold text-gray-900">{order.campaign}</h4>
                  <p className="text-sm text-gray-600">{order.seasonYear} Season</p>
                </div>
                {selectedPreviousOrder === order.orderId && (
                  <CheckCircle className="w-5 h-5 text-hhg-primary" />
                )}
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">{order.totalItems} items</span>
                <span className="font-semibold text-gray-900">${order.totalValue.toLocaleString()}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* AI Mapping Result */}
      {loading && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hhg-primary mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">AI is mapping items to current catalog...</p>
        </div>
      )}

      {!loading && cart.length > 0 && selectedOrder && (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-green-900 mb-1">Order Successfully Reconstructed</h4>
              <p className="text-sm text-green-700">
                Mapped {cart.length} items from "{selectedOrder.campaign}" to current catalog.
                Review quantities and finalize your cart below.
              </p>
            </div>
          </div>

          {/* Mapped Items Table */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">AI-Mapped Cart Items</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Original Item
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Mapped To
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Confidence
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Price
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {cart.map((item, idx) => (
                    <tr key={idx}>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <div className="font-medium text-gray-900">{item.mappedFrom?.itemName}</div>
                          <div className="text-gray-500">{item.mappedFrom?.legacyItemId}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <div className="font-medium text-gray-900">{item.catalogItem.name}</div>
                          <div className="text-gray-500">{item.catalogItem.id}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          (item.matchConfidence || 0) > 90
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {item.matchConfidence}% match
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <input
                          type="number"
                          value={item.suggestedQuantity}
                          onChange={(e) => updateCartItem(idx, { suggestedQuantity: parseInt(e.target.value), userAdjusted: true })}
                          className="w-24 px-3 py-2 border border-gray-300 rounded-md text-sm"
                          min={item.catalogItem.minOrderQty}
                        />
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          ${(item.catalogItem.unitPrice * item.suggestedQuantity).toLocaleString()}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Cart Summary & Actions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">Cart Summary</h3>
                <p className="text-sm text-gray-600">
                  {cart.length} items • Estimated Total: ${cart.reduce((sum, item) => 
                    sum + (item.catalogItem.unitPrice * item.suggestedQuantity), 0
                  ).toLocaleString()}
                </p>
              </div>
              <button className="bg-hhg-primary text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition inline-flex items-center space-x-2">
                <span>Finalize Order</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
