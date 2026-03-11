import { Database, Cloud, Cpu, GitBranch, ArrowRight } from 'lucide-react'

export default function Architecture() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Technical Architecture</h2>
        <p className="text-gray-600">
          Understanding the path from rapid prototype to enterprise-ready AI solution
        </p>
      </div>

      {/* Current Demo Architecture */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="mb-6">
          <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded-full mb-4">
            Current Demo (Static PoC)
          </span>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Rapid Prototype Architecture</h3>
          <p className="text-gray-600">
            Built for speed and low delivery risk with static data and deterministic logic
          </p>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Cloud className="w-6 h-6 text-hhg-primary" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Static Hosting</h4>
            <p className="text-sm text-gray-600">
              React SPA on GCP Storage with CDN distribution
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Database className="w-6 h-6 text-purple-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">JSON Data</h4>
            <p className="text-sm text-gray-600">
              Synthetic demo data in static JSON files
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <Cpu className="w-6 h-6 text-green-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Deterministic Logic</h4>
            <p className="text-sm text-gray-600">
              Rule-based "AI" for predictable demo behavior
            </p>
          </div>
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h5 className="font-semibold text-blue-900 mb-2">Why This Approach?</h5>
          <ul className="space-y-1 text-sm text-blue-800">
            <li>• Zero backend infrastructure = faster delivery</li>
            <li>• No live AI dependencies = stable, reproducible demos</li>
            <li>• Static hosting = simple deployment, low cost</li>
            <li>• Clear separation of concerns = easy pilot migration</li>
          </ul>
        </div>
      </div>

      {/* Pilot Architecture */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="mb-6">
          <span className="inline-block px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full mb-4">
            Phase 1 Pilot (4-6 Weeks)
          </span>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Production Pilot Architecture</h3>
          <p className="text-gray-600">
            Integration with real systems while maintaining architectural clarity
          </p>
        </div>

        <div className="space-y-4">
          {/* Source Systems */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <Database className="w-5 h-5 mr-2 text-gray-600" />
              Source Systems Layer
            </h4>
            <div className="grid grid-cols-4 gap-3">
              {['Catalog DB', 'Order Management', 'Supplier Master', 'Warehouse'].map(system => (
                <div key={system} className="bg-gray-100 rounded p-3 text-center text-sm font-medium text-gray-700">
                  {system}
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-center">
            <ArrowRight className="w-6 h-6 text-gray-400 rotate-90" />
          </div>

          {/* Intelligence Layer */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <Cpu className="w-5 h-5 mr-2 text-purple-600" />
              Intelligence Layer
            </h4>
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-purple-50 border border-purple-200 rounded p-4">
                <h5 className="font-semibold text-sm text-purple-900 mb-1">Item Mapper</h5>
                <p className="text-xs text-purple-700">Legacy→Current catalog matching via embeddings</p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded p-4">
                <h5 className="font-semibold text-sm text-purple-900 mb-1">Risk Analyzer</h5>
                <p className="text-xs text-purple-700">Overstock & deadline risk scoring</p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded p-4">
                <h5 className="font-semibold text-sm text-purple-900 mb-1">Supplier Recommender</h5>
                <p className="text-xs text-purple-700">Performance-based supplier ranking</p>
              </div>
            </div>
          </div>

          <div className="flex justify-center">
            <ArrowRight className="w-6 h-6 text-gray-400 rotate-90" />
          </div>

          {/* Workflow Layer */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <GitBranch className="w-5 h-5 mr-2 text-green-600" />
              Workflow Layer
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-green-50 border border-green-200 rounded p-4">
                <h5 className="font-semibold text-sm text-green-900 mb-1">Buy Window API</h5>
                <p className="text-xs text-green-700">Order reconstruction & cart management</p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded p-4">
                <h5 className="font-semibold text-sm text-green-900 mb-1">Risk Co-Pilot API</h5>
                <p className="text-xs text-green-700">Risk assessment & RFQ generation</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
          <h5 className="font-semibold text-green-900 mb-2">Pilot Migration Benefits</h5>
          <ul className="space-y-1 text-sm text-green-800">
            <li>• Frontend components remain largely unchanged</li>
            <li>• Intelligence layer can use OpenAI, Claude, or custom models</li>
            <li>• Source system integration via standard REST APIs</li>
            <li>• Incremental rollout: start with one workflow</li>
          </ul>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">Technology Stack</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Frontend</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center">
                <span className="w-2 h-2 bg-hhg-primary rounded-full mr-2"></span>
                React 18 + TypeScript
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-hhg-primary rounded-full mr-2"></span>
                Tailwind CSS for styling
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-hhg-primary rounded-full mr-2"></span>
                Zustand for state management
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-hhg-primary rounded-full mr-2"></span>
                Recharts for visualizations
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Pilot Backend (Future)</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                Node.js/Python for API layer
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                PostgreSQL for structured data
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                Vector DB for embeddings
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                LLM APIs (OpenAI/Claude/Custom)
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Integration Points */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">Integration Requirements for Pilot</h3>
        <div className="space-y-4">
          {[
            {
              system: 'Product Catalog API',
              data: 'Current item IDs, specs, pricing, supplier codes',
              format: 'REST API or CSV export',
              frequency: 'Daily sync'
            },
            {
              system: 'Order History',
              data: 'Past 2-3 years of seasonal orders with item mappings',
              format: 'Database query or JSON extract',
              frequency: 'One-time + incremental'
            },
            {
              system: 'Supplier Performance',
              data: 'On-time delivery rates, quality scores, pricing',
              format: 'Analytics DB or reporting API',
              frequency: 'Weekly'
            },
            {
              system: 'Event Calendar',
              data: 'Campaign dates, expected attendee counts',
              format: 'REST API or calendar feed',
              frequency: 'Real-time'
            }
          ].map((integration, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-1">{integration.system}</h4>
                  <p className="text-sm text-gray-600 mb-2">{integration.data}</p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span><strong>Format:</strong> {integration.format}</span>
                    <span>•</span>
                    <span><strong>Frequency:</strong> {integration.frequency}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-hhg-primary to-blue-700 rounded-lg shadow-lg p-8 text-white text-center">
        <h3 className="text-2xl font-bold mb-3">Ready to Move from Demo to Pilot?</h3>
        <p className="text-lg opacity-90 mb-6 max-w-2xl mx-auto">
          This architecture supports a phased, low-risk path from static prototype to production AI workflow.
        </p>
        <p className="opacity-90">
          Let's discuss integration requirements and pilot scope.
        </p>
      </div>
    </div>
  )
}
