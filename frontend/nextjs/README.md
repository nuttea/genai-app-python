# Next.js Frontend - Datadog GenAI Platform

Modern Next.js frontend application for the Datadog GenAI Platform with Datadog purple theme and extensible architecture.

## 🚀 Features

- ✨ Modern, responsive UI with Datadog branding
- 🎯 Sidebar navigation for multiple GenAI services
- 🔌 Routes to Cloud Run backend APIs
- 📱 Mobile-friendly design
- 🚀 Server-side rendering (SSR) with Next.js 14
- 🎨 Component-based architecture with TypeScript
- 📊 Datadog RUM integration for monitoring

## 🏗️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom Datadog theme
- **UI Components**: Custom components + Radix UI primitives
- **Icons**: Lucide React
- **HTTP Client**: Axios with SWR
- **Monitoring**: Datadog RUM

## 📋 Prerequisites

- Node.js >= 20.0.0
- npm >= 10.0.0

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Update .env.local with your values
```

## 🚀 Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

The page will auto-reload when you make changes.

## 📦 Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## 🧪 Testing

```bash
# Run type checking
npm run type-check

# Run linting
npm run lint

# Format code
npm run format
```

## 🐳 Docker

### Local Development

```bash
# Build Docker image
docker build -t nextjs-frontend .

# Run container
docker run -p 3000:3000 nextjs-frontend
```

### Docker Compose

```bash
# Start all services
docker-compose up nextjs-frontend

# Or start with backend services
docker-compose up
```

## 🌍 Environment Variables

See `.env.example` for all available environment variables:

- `NEXT_PUBLIC_APP_NAME` - Application name
- `NEXT_PUBLIC_VOTE_EXTRACTOR_API` - Vote Extractor API URL
- `NEXT_PUBLIC_CONTENT_CREATOR_API` - Content Creator API URL
- `NEXT_PUBLIC_DD_APPLICATION_ID` - Datadog application ID
- `NEXT_PUBLIC_DD_CLIENT_TOKEN` - Datadog client token

## 📁 Project Structure

```
frontend/nextjs/
├── app/                      # Next.js 14 App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard page
│   ├── error.tsx            # Error boundary
│   ├── loading.tsx          # Loading state
│   ├── vote-extractor/      # Vote Extractor pages
│   ├── content-creator/     # Content Creator pages
│   └── api/                 # API routes (proxy)
├── components/
│   ├── layout/              # Sidebar, Header
│   ├── ui/                  # Reusable UI components
│   ├── services/            # Service-specific components
│   └── shared/              # Shared components
├── lib/
│   ├── api/                 # API client functions
│   ├── utils/               # Helper functions
│   └── constants/           # Constants (colors, config)
├── styles/
│   └── globals.css          # Global styles
├── public/                  # Static assets
└── types/                   # TypeScript types
```

## 🎨 Datadog Theme

The application uses Datadog's official color palette:

- **Primary**: Purple (#774AA4)
- **Secondary**: Dark Purple (#632D91)
- **Success**: Green (#27AE60)
- **Warning**: Orange (#F39C12)
- **Error**: Red (#E74C3C)
- **Info**: Blue (#3498DB)

## 🔗 Adding New Services

To add a new GenAI service to the sidebar:

1. **Add to sidebar**:
```typescript
// components/layout/Sidebar.tsx
const services = [
  // ... existing services
  { name: 'Your Service', icon: YourIcon, href: '/your-service' },
];
```

2. **Create page**:
```typescript
// app/your-service/page.tsx
export default function YourServicePage() {
  return <div>Your Service Content</div>;
}
```

3. **Add API client** (if needed):
```typescript
// lib/api/yourService.ts
export const yourServiceApi = {
  // API functions
};
```

## 📊 Datadog RUM Monitoring

The application includes Datadog Real User Monitoring:

- Session recording (optional)
- User interactions tracking
- Resource and long task tracking
- Automatic error tracking

Configure in `.env.local`:

```bash
NEXT_PUBLIC_DD_APPLICATION_ID=your-app-id
NEXT_PUBLIC_DD_CLIENT_TOKEN=your-client-token
NEXT_PUBLIC_DD_SESSION_REPLAY_ENABLED=true
```

## 🚢 Deployment

### Cloud Run

```bash
# Build for Cloud Run
npm run build

# Deploy
gcloud run deploy nextjs-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

See `.github/workflows/nextjs-frontend.yml` for automated CI/CD.

## 📚 Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [Implementation Plan](../../docs/features/NEXTJS_FRONTEND_PLAN.md)
- [Project Documentation](../../DOCUMENTATION_MAP.md)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run `npm run lint` and `npm run type-check`
4. Submit a pull request

## 📝 License

See the main project LICENSE file.

---

**Status**: 🚧 In Development

**Version**: 1.0.0

