import { Database, FileJson, TrendingUp, AlertCircle } from 'lucide-react'

export default function DataStory() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Understanding the Demo Data</h2>
        <p className="text-gray-600">
          This demo uses synthetic but realistic data designed to showcase AI capabilities.
          Here's what's powering the intelligence you see.
        </p>
      </div>

      {/* Important Notice */}
      <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-900 mb-2">Demo Data Notice</h3>
            <p className="text-sm text-yellow-800">
              All data in this demonstration is <strong>synthetic and for illustrative purposes only</strong>.
              It's designed to represent realistic patterns and business scenarios without exposing actual
              client or operational data.
            </p>
          </div>
        </div>
      </div>

      {/* Data Sources */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <FileJson className="w-6 h-6 mr-2 text-hhg-primary" />
          Current Demo Data Sources
        </h3>
        <div className="space-y-4">
          {[
            {
              file: 'catalog.json',
              records: '8 items',
              purpose: 'Current product catalog with pricing, suppliers, and lead times',
              keyFields: ['Item ID', 'Name', 'Category', 'Unit Price', 'Supplier Code', 'Lead Time Days']
            },
            {
              file: 'previous-orders.json',
              records: '2 orders',
              purpose: 'Historical seasonal orders for AI mapping reconstruction',
              keyFields: ['Order ID', 'Campaign', 'Season Year', 'Legacy Item IDs', 'Quantities']
            },
            {
              file: 'orders.json',
              records: '2 pending orders',
              purpose: 'Incoming orders requiring risk assessment and procurement decisions',
              keyFields: ['Order ID', 'Campaign', 'Event Date', 'Items', 'Total Value']
            },
            {
              file: 'risk-assessment.json',
              records: '1 assessment',
              purpose: 'AI-generated risk analysis for high-risk order ORD-2026-043',
              keyFields: ['Risk Type', 'Severity', 'Impact', 'Recommendations', 'Supplier Analysis']
            },
            {
              file: 'rfq-draft.json',
              records: '1 RFQ',
              purpose: 'Auto-generated RFQ for supplier switching recommendations',
              keyFields: ['RFQ ID', 'Suppliers', 'Items', 'Special Requirements', 'Deadline']
            }
          ].map((source, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">{source.file}</h4>
                  <p className="text-sm text-gray-600">{source.purpose}</p>
                </div>
                <span className="bg-gray-100 px-3 py-1 rounded-full text-xs font-medium text-gray-700">
                  {source.records}
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {source.keyFields.map(field => (
                  <span key={field} className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs font-medium">
                    {field}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Logic Explained */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <TrendingUp className="w-6 h-6 mr-2 text-purple-600" />
          How the "AI" Works in This Demo
        </h3>
        <div className="space-y-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Smart Buy Window Co-Pilot</h4>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-gray-700 mb-3">
                <strong>Deterministic matching logic:</strong>
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">1.</span>
                  <span>Maps legacy item categories to current catalog categories</span>
                </li>
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">2.</span>
                  <span>Assigns 95% confidence for exact category match, 75% for fuzzy match</span>
                </li>
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">3.</span>
                  <span>Preserves original quantities as suggested values</span>
                </li>
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">4.</span>
                  <span>Displays mapping rationale in the UI</span>
                </li>
              </ul>
              <p className="text-xs text-blue-700 mt-3">
                <strong>In production:</strong> Would use semantic embeddings and LLM-based reasoning for
                true fuzzy matching across product descriptions.
              </p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Order Execution & Risk Co-Pilot</h4>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <p className="text-sm text-gray-700 mb-3">
                <strong>Risk detection rules:</strong>
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">1.</span>
                  <span>Flags overstock if order quantity exceeds historical pickup rate by 20%</span>
                </li>
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">2.</span>
                  <span>Flags deadline risk if (event date - today) &lt; (lead time + 7 day buffer)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">3.</span>
                  <span>Recommends supplier if overall score &gt; current + 0.3 points</span>
                </li>
                <li className="flex items-start">
                  <span className="text-hhg-primary mr-2">4.</span>
                  <span>Generates RFQ draft with templated requirements</span>
                </li>
              </ul>
              <p className="text-xs text-orange-700 mt-3">
                <strong>In production:</strong> Would integrate real forecast models, warehouse data,
                and ML-based supplier performance predictions.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Real Data Requirements */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <Database className="w-6 h-6 mr-2 text-green-600" />
          Real Data Needed for Production Pilot
        </h3>
        <div className="grid grid-cols-2 gap-6">
          <div className="border border-gray-200 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-3">Historical Order Data</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• 2-3 years of seasonal campaign orders</li>
              <li>• Item-level details with quantities and fulfillment dates</li>
              <li>• Actual vs. forecasted demand for events</li>
              <li>• Post-event surplus/shortage reports</li>
            </ul>
            <p className="text-xs text-gray-500 mt-3 italic">
              Used to train overstock prediction models
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-3">Product Catalog</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Current active catalog items with SKUs</li>
              <li>• Product descriptions and specifications</li>
              <li>• Pricing, supplier codes, lead times</li>
              <li>• Legacy item ID mappings if available</li>
            </ul>
            <p className="text-xs text-gray-500 mt-3 italic">
              Used for semantic matching and availability checks
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-3">Supplier Performance</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• On-time delivery rates by supplier</li>
              <li>• Quality incident logs</li>
              <li>• Historical pricing variations</li>
              <li>• Capacity and lead time data</li>
            </ul>
            <p className="text-xs text-gray-500 mt-3 italic">
              Used for supplier recommendation algorithms
            </p>
          </div>

          <div className="border border-gray-200 rounded-lg p-5">
            <h4 className="font-semibold text-gray-900 mb-3">Event & Campaign Data</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Upcoming campaign calendar with dates</li>
              <li>• Expected attendee/recipient counts</li>
              <li>• Event type classifications</li>
              <li>• Historical pickup/usage rates by event type</li>
            </ul>
            <p className="text-xs text-gray-500 mt-3 italic">
              Used for demand forecasting and deadline analysis
            </p>
          </div>
        </div>
      </div>

      {/* Data Privacy */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Data Privacy & Security</h3>
        <div className="space-y-4 text-sm text-gray-600">
          <p>
            For a production pilot, we would work closely with your IT and data governance teams to ensure:
          </p>
          <ul className="space-y-2 ml-5">
            <li className="flex items-start">
              <span className="text-hhg-primary mr-2">•</span>
              <span><strong>Data minimization:</strong> Only request data fields truly needed for intelligence</span>
            </li>
            <li className="flex items-start">
              <span className="text-hhg-primary mr-2">•</span>
              <span><strong>Anonymization:</strong> Remove PII where possible (e.g., client names can be tokenized)</span>
            </li>
            <li className="flex items-start">
              <span className="text-hhg-primary mr-2">•</span>
              <span><strong>Secure transfer:</strong> Encrypted data exchange and secure API authentication</span>
            </li>
            <li className="flex items-start">
              <span className="text-hhg-primary mr-2">•</span>
              <span><strong>Compliance:</strong> Adhere to GDPR, SOC2, or other relevant data protection standards</span>
            </li>
            <li className="flex items-start">
              <span className="text-hhg-primary mr-2">•</span>
              <span><strong>Audit trail:</strong> Full logging of data access and AI decision rationale</span>
            </li>
          </ul>
        </div>
      </div>

      {/* CTA */}
      <div className="bg-gray-100 rounded-lg p-6 text-center">
        <h3 className="text-lg font-bold text-gray-900 mb-2">
          Questions About Data Requirements?
        </h3>
        <p className="text-sm text-gray-600">
          We're happy to discuss specific data sources, integration formats, and privacy considerations
          during a pilot design workshop.
        </p>
      </div>
    </div>
  )
}
