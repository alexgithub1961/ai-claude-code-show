// Catalog Item
export interface CatalogItem {
  id: string
  name: string
  category: string
  description: string
  unitPrice: number
  currency: string
  supplierCode: string
  leadTimeDays: number
  minOrderQty: number
  available: boolean
  imageUrl?: string
}

// Previous Season Order
export interface PreviousOrderItem {
  legacyItemId: string
  itemName: string
  quantity: number
  unitPrice: number
  category: string
}

export interface PreviousOrder {
  orderId: string
  seasonYear: number
  campaign: string
  totalItems: number
  totalValue: number
  items: PreviousOrderItem[]
  completedDate: string
}

// Mapped Cart Item (AI-suggested mapping)
export interface CartItem {
  catalogItem: CatalogItem
  suggestedQuantity: number
  mappedFrom?: PreviousOrderItem
  matchConfidence?: number
  userAdjusted: boolean
}

// Order with Risk Assessment
export interface Order {
  orderId: string
  campaign: string
  client: string
  eventDate: string
  totalValue: number
  items: OrderItem[]
  createdDate: string
  status: string
}

export interface OrderItem {
  catalogItemId: string
  catalogItemName: string
  quantity: number
  unitPrice: number
  supplierCode: string
  leadTimeDays: number
}

// Risk Assessment
export interface RiskAssessment {
  orderId: string
  overallRiskLevel: 'low' | 'medium' | 'high' | 'critical'
  risks: Risk[]
  recommendations: Recommendation[]
  supplierAnalysis: SupplierScore[]
}

export interface Risk {
  type: 'overstock' | 'deadline' | 'supplier' | 'demand'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  impact: string
  affectedItems?: string[]
}

export interface Recommendation {
  type: 'reduce-quantity' | 'split-order' | 'expedite' | 'alternative-supplier' | 'defer'
  title: string
  description: string
  expectedImpact: string
  actionItems: string[]
}

export interface SupplierScore {
  supplierCode: string
  supplierName: string
  onTimeRate: number
  qualityScore: number
  priceCompetitiveness: number
  overallScore: number
  recommendedForItems: string[]
}

// RFQ Draft
export interface RFQDraft {
  rfqId: string
  orderId: string
  suppliers: string[]
  items: RFQItem[]
  deadline: string
  specialRequirements: string[]
  generatedAt: string
}

export interface RFQItem {
  catalogItemId: string
  itemName: string
  quantity: number
  requiredBy: string
  specifications: string[]
}
