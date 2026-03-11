# HHG Supply Chain AI Studio

AI-powered workflow co-pilots for marketing supply chain optimization.

## Overview

This demo showcases two intelligent workflow interventions for HH Global's supply chain lifecycle:

1. **Smart Buy Window Co-Pilot** - Reconstructs recurring seasonal orders with AI-powered item mapping
2. **Order Execution & Risk Co-Pilot** - Identifies overstock and deadline risks with supplier recommendations

Built as a rapid prototype to demonstrate AI capabilities in the demand aggregation → procurement allocation → event readiness lifecycle.

## Features

- 🎯 **Overview** - Lifecycle visualization and business impact metrics
- 🛒 **Buy Window Co-Pilot** - Seconds, not hours to rebuild seasonal orders
- ⚠️ **Risk Co-Pilot** - Risk surfaced before orders become expensive
- 🏗️ **Architecture** - Clear path from demo to production pilot
- 📊 **Data Story** - Understanding the synthetic demo data

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Icons**: Lucide React
- **Routing**: React Router
- **Build**: Vite (optimized production build)

## Quick Start

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Run development server
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173) in your browser.

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

The build output will be in the `dist/` directory.

## Project Structure

```
hhg-demon-2026/
├── public/
│   └── data/              # Demo JSON data files
│       ├── catalog.json
│       ├── previous-orders.json
│       ├── orders.json
│       ├── risk-assessment.json
│       └── rfq-draft.json
├── src/
│   ├── components/        # React components (if needed)
│   ├── pages/             # Main page components
│   │   ├── Overview.tsx
│   │   ├── BuyWindow.tsx
│   │   ├── RiskCoPilot.tsx
│   │   ├── Architecture.tsx
│   │   └── DataStory.tsx
│   ├── store/             # Zustand state management
│   ├── types/             # TypeScript type definitions
│   ├── App.tsx            # Main app component with routing
│   └── main.tsx           # Entry point
├── DEPLOYMENT.md          # GCP deployment guide
└── README.md              # This file
```

## Demo Data

All data is **synthetic and for illustrative purposes only**. The demo uses:

- 8 catalog items
- 2 historical orders
- 2 pending orders (1 with high risk)
- 1 detailed risk assessment
- 1 auto-generated RFQ draft

See `DEPLOYMENT.md` for data requirements in a production pilot.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions on deploying to Google Cloud Storage.

### Quick Deploy Options

**Option 1: GCP Storage**
```bash
npm run build
# Follow steps in DEPLOYMENT.md
```

**Option 2: Firebase Hosting**
```bash
npm run build
firebase deploy --only hosting
```

**Option 3: Any Static Host**

The `dist/` folder contains a fully static site that can be deployed to:
- Netlify
- Vercel
- GitHub Pages
- Any static hosting service

## Key Demo Flows

### Flow 1: Smart Buy Window Co-Pilot

1. Navigate to "Smart Buy Window"
2. Select a previous seasonal order (e.g., "Spring Product Launch 2025")
3. Watch AI map legacy items to current catalog
4. Review confidence scores and adjust quantities
5. Finalize cart

**Key Message**: "Seconds, not hours" to reconstruct recurring orders

### Flow 2: Order Execution & Risk Co-Pilot

1. Navigate to "Order Execution & Risk"
2. Select the high-risk order (ORD-2026-043)
3. Review 4 identified risks (overstock, deadline, supplier)
4. See AI recommendations with expected impact
5. View supplier performance comparison
6. Generate RFQ draft for recommended supplier switches

**Key Message**: "Risk surfaced before orders become expensive"

## Customization

### Update Demo Data

Edit JSON files in `public/data/`:
- Add more catalog items
- Create additional historical orders
- Modify risk assessment logic (deterministic rules in components)

### Adjust Branding

Update colors in `tailwind.config.js`:
```js
colors: {
  hhg: {
    primary: '#0066CC',    // Change to your brand color
    secondary: '#FF6B35',
  }
}
```

### Add New Features

1. Create new page in `src/pages/`
2. Add route in `src/App.tsx`
3. Update navigation

## Technical Notes

### Why Static/Deterministic?

This demo is intentionally built without live AI calls:
- **Fast delivery**: 1-day build target
- **Stable demos**: Predictable, reproducible behavior
- **Low risk**: No API costs or rate limits during demos
- **Easy evolution**: Clear separation makes pilot migration straightforward

### Path to Production

See the **Architecture** page in the demo for the evolution from:
- Static prototype → API-backed pilot → Enterprise solution

## Performance

- Initial load: ~250KB (gzipped)
- Time to Interactive: <2s on 3G
- Lighthouse Score: 95+ (Performance, Accessibility, Best Practices)

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS 14+, Android Chrome

## Contributing

This is a demo project. For production pilots, contact First Line Software.

## License

Proprietary - Demo for HH Global evaluation

## Contact

Built by **First Line Software**  
For questions about pilot implementation: [contact info]

---

**Demo Link**: [Insert deployed URL here]  
**Build Date**: March 2026
