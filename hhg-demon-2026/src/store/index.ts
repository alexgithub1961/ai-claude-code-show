import { create } from 'zustand'
import { CartItem, RiskAssessment, RFQDraft } from '../types'

interface AppState {
  // Smart Buy Window
  selectedPreviousOrder: string | null
  cart: CartItem[]
  setSelectedPreviousOrder: (orderId: string | null) => void
  setCart: (cart: CartItem[]) => void
  updateCartItem: (index: number, updates: Partial<CartItem>) => void
  removeCartItem: (index: number) => void
  
  // Risk Co-Pilot
  selectedOrder: string | null
  currentRiskAssessment: RiskAssessment | null
  currentRFQDraft: RFQDraft | null
  setSelectedOrder: (orderId: string | null) => void
  setRiskAssessment: (assessment: RiskAssessment | null) => void
  setRFQDraft: (draft: RFQDraft | null) => void
}

export const useStore = create<AppState>((set) => ({
  // Smart Buy Window
  selectedPreviousOrder: null,
  cart: [],
  setSelectedPreviousOrder: (orderId) => set({ selectedPreviousOrder: orderId }),
  setCart: (cart) => set({ cart }),
  updateCartItem: (index, updates) => set((state) => ({
    cart: state.cart.map((item, i) => 
      i === index ? { ...item, ...updates } : item
    )
  })),
  removeCartItem: (index) => set((state) => ({
    cart: state.cart.filter((_, i) => i !== index)
  })),
  
  // Risk Co-Pilot
  selectedOrder: null,
  currentRiskAssessment: null,
  currentRFQDraft: null,
  setSelectedOrder: (orderId) => set({ selectedOrder: orderId }),
  setRiskAssessment: (assessment) => set({ currentRiskAssessment: assessment }),
  setRFQDraft: (draft) => set({ currentRFQDraft: draft }),
}))
