# 🎨 Next.js Frontend - Modern GenAI Application Hub

## Overview

A modern, production-ready Next.js web application that serves as a unified hub for multiple GenAI prototype services, featuring Datadog's brand colors and a scalable sidebar architecture.

**Key Features**:
- ✨ Modern UI with Datadog color theme
- 🎯 Sidebar navigation for multiple GenAI services
- 🔌 Routes to backend APIs on Cloud Run
- 📱 Responsive design (mobile, tablet, desktop)
- ⚡ Server-side rendering (SSR) with Next.js 14+
- 🎨 Tailwind CSS + shadcn/ui components
- 🔐 Authentication ready (optional)

---

## 🏗️ Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                          │
│                   (Cloud Run Service)                        │
│                                                               │
│  ┌────────────────┐  ┌──────────────────────────┐          │
│  │  Sidebar Nav   │  │   Main Content Area       │          │
│  │                │  │                            │          │
│  │  📊 Dashboard  │  │  🗳️ Vote Extractor        │          │
│  │  🗳️ Votes      │  │  📝 Content Creator       │          │
│  │  📝 Content    │  │  🤖 [Future Services]     │          │
│  │  ➕ Add New    │  │                            │          │
│  └────────────────┘  └──────────────────────────┘          │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────────┐
        │      API Layer (Client-Side Fetch)        │
        └───────────────────────────┬───────────────┘
                                    │
        ┌───────────────────────────┴───────────────────────┐
        │                                                     │
        ▼                                                     ▼
┌──────────────────┐                             ┌──────────────────┐
│  Vote Extractor  │                             │ Content Creator  │
│    Backend API   │                             │   Backend API    │
│  (Cloud Run)     │                             │  (Cloud Run)     │
│                  │                             │                  │
│ /api/v1/extract  │                             │ /api/v1/generate │
│ /api/v1/models   │                             │ /api/v1/upload   │
└──────────────────┘                             └──────────────────┘
```

---

## 📁 Project Structure

```
genai-app-python/
├── frontend/
│   └── nextjs-web/                    # 🆕 NEW NEXT.JS APP
│       ├── app/                       # Next.js 14 App Router
│       │   ├── layout.tsx            # Root layout with sidebar
│       │   ├── page.tsx              # Dashboard home
│       │   ├── votes/                # Vote Extractor pages
│       │   │   ├── page.tsx          # Main vote extraction
│       │   │   └── history/
│       │   │       └── page.tsx      # Extraction history
│       │   ├── content/              # Content Creator pages
│       │   │   ├── page.tsx          # Content generation
│       │   │   ├── blog/
│       │   │   │   └── page.tsx      # Blog post creator
│       │   │   ├── video/
│       │   │   │   └── page.tsx      # Video script creator
│       │   │   └── social/
│       │   │       └── page.tsx      # Social media posts
│       │   └── api/                  # API routes (optional proxy)
│       │       └── [...proxy].ts     # Proxy to Cloud Run
│       │
│       ├── components/               # React components
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx       # Main sidebar navigation
│       │   │   ├── Header.tsx        # Top header
│       │   │   └── Footer.tsx        # Footer
│       │   ├── ui/                   # shadcn/ui components
│       │   │   ├── button.tsx
│       │   │   ├── card.tsx
│       │   │   ├── input.tsx
│       │   │   └── ...
│       │   ├── votes/
│       │   │   ├── FileUploader.tsx
│       │   │   ├── ExtractionForm.tsx
│       │   │   └── ResultsDisplay.tsx
│       │   └── content/
│       │       ├── ContentTypeSelector.tsx
│       │       ├── BlogEditor.tsx
│       │       └── VideoScriptEditor.tsx
│       │
│       ├── lib/                      # Utilities
│       │   ├── api/
│       │   │   ├── votes.ts          # Vote API client
│       │   │   └── content.ts        # Content API client
│       │   ├── theme.ts              # Datadog color theme
│       │   └── utils.ts              # Helper functions
│       │
│       ├── public/                   # Static assets
│       │   ├── logo.svg
│       │   └── icons/
│       │
│       ├── styles/
│       │   └── globals.css           # Global styles (Tailwind)
│       │
│       ├── .env.local                # Environment variables
│       ├── .env.production           # Production env vars
│       ├── next.config.js            # Next.js configuration
│       ├── tailwind.config.ts        # Tailwind + Datadog theme
│       ├── tsconfig.json             # TypeScript config
│       ├── package.json              # Dependencies
│       ├── Dockerfile                # Docker for Cloud Run
│       └── README.md
│
└── services/
    ├── fastapi-backend/              # Vote Extractor API
    └── adk-content-creator/          # Content Creator API
```

---

## 🎨 Datadog Color Theme

### Primary Colors

```typescript
// lib/theme.ts
export const datadogTheme = {
  colors: {
    // Primary Datadog Purple
    primary: {
      50: '#F5F3FF',
      100: '#EDE9FE',
      200: '#DDD6FE',
      300: '#C4B5FD',
      400: '#A78BFA',
      500: '#8B5CF6',  // Main Datadog purple
      600: '#7C3AED',
      700: '#6D28D9',
      800: '#5B21B6',
      900: '#4C1D95',
    },
    
    // Datadog Pink/Magenta
    secondary: {
      500: '#D946EF',
      600: '#C026D3',
      700: '#A21CAF',
    },
    
    // Success (Green)
    success: {
      500: '#10B981',
      600: '#059669',
    },
    
    // Warning (Orange)
    warning: {
      500: '#F59E0B',
      600: '#D97706',
    },
    
    // Error (Red)
    error: {
      500: '#EF4444',
      600: '#DC2626',
    },
    
    // Neutral (Grays)
    neutral: {
      50: '#F9FAFB',
      100: '#F3F4F6',
      200: '#E5E7EB',
      300: '#D1D5DB',
      400: '#9CA3AF',
      500: '#6B7280',
      600: '#4B5563',
      700: '#374151',
      800: '#1F2937',
      900: '#111827',
    },
  },
}
```

### Tailwind Configuration

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'
import { datadogTheme } from './lib/theme'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        ...datadogTheme.colors,
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

---

## 🧩 Key Components

### 1. Sidebar Navigation

```typescript
// components/layout/Sidebar.tsx
export function Sidebar() {
  const services = [
    {
      name: 'Dashboard',
      icon: LayoutDashboard,
      href: '/',
      description: 'Overview of all services'
    },
    {
      name: 'Vote Extractor',
      icon: FileText,
      href: '/votes',
      description: 'Extract election vote data from PDFs'
    },
    {
      name: 'Content Creator',
      icon: Sparkles,
      href: '/content',
      description: 'Generate blog posts & video scripts'
    },
    {
      name: 'Add New Service',
      icon: Plus,
      href: '/services/new',
      description: 'Add a new GenAI prototype'
    },
  ]
  
  return (
    <aside className="w-64 bg-neutral-900 text-white border-r border-neutral-800">
      {/* Logo */}
      <div className="p-6 border-b border-neutral-800">
        <h1 className="text-2xl font-bold text-primary-500">
          GenAI Hub
        </h1>
        <p className="text-sm text-neutral-400 mt-1">
          Datadog Prototypes
        </p>
      </div>
      
      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {services.map((service) => (
          <Link
            key={service.href}
            href={service.href}
            className="flex items-center gap-3 px-4 py-3 rounded-lg
                       hover:bg-primary-600 transition-colors"
          >
            <service.icon className="w-5 h-5" />
            <div>
              <div className="font-medium">{service.name}</div>
              <div className="text-xs text-neutral-400">
                {service.description}
              </div>
            </div>
          </Link>
        ))}
      </nav>
    </aside>
  )
}
```

### 2. API Client

```typescript
// lib/api/content.ts
export class ContentAPI {
  private baseURL: string
  
  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_CONTENT_API_URL || 
                   'http://localhost:8002'
  }
  
  async generateBlogPost(request: BlogPostRequest): Promise<BlogPost> {
    const response = await fetch(`${this.baseURL}/api/v1/generate/blog-post`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to generate blog post: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${this.baseURL}/api/v1/upload/file`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      throw new Error(`Failed to upload file: ${response.statusText}`)
    }
    
    return response.json()
  }
}

export const contentAPI = new ContentAPI()
```

---

## 📋 Implementation Phases

### Phase 1: Foundation (Week 1)

#### 1.1 Project Setup
- [ ] Create Next.js 14 project with TypeScript
- [ ] Configure Tailwind CSS with Datadog theme
- [ ] Install shadcn/ui components
- [ ] Set up project structure
- [ ] Configure Docker for Cloud Run

**Commands:**
```bash
# Create Next.js project
npx create-next-app@latest frontend/nextjs-web \
  --typescript \
  --tailwind \
  --app \
  --src-dir=false \
  --import-alias="@/*"

# Install dependencies
cd frontend/nextjs-web
npm install @radix-ui/react-* class-variance-authority clsx tailwind-merge
npm install lucide-react  # Icons
npm install @tanstack/react-query  # Data fetching
npm install zustand  # State management

# Install shadcn/ui
npx shadcn-ui@latest init
```

#### 1.2 Datadog Theme Configuration
- [ ] Create theme configuration file
- [ ] Configure Tailwind with Datadog colors
- [ ] Set up custom fonts (Inter, JetBrains Mono)
- [ ] Create global CSS with theme variables

#### 1.3 Layout Components
- [ ] Create Sidebar component
- [ ] Create Header component
- [ ] Create Footer component
- [ ] Create root layout with sidebar

### Phase 2: Dashboard & Navigation (Week 2)

#### 2.1 Dashboard Page
- [ ] Create dashboard home page
- [ ] Add service cards/overview
- [ ] Add recent activity feed
- [ ] Add quick actions

#### 2.2 Navigation System
- [ ] Implement sidebar navigation
- [ ] Add active state indicators
- [ ] Add breadcrumbs
- [ ] Add mobile responsive menu

#### 2.3 Service Management
- [ ] Create "Add New Service" page
- [ ] Service card template
- [ ] Service configuration form

### Phase 3: Vote Extractor Integration (Week 3)

#### 3.1 Vote Extractor Pages
- [ ] Main extraction page (`/votes`)
- [ ] File upload interface
- [ ] LLM configuration panel
- [ ] Results display component

#### 3.2 API Integration
- [ ] Create Vote Extractor API client
- [ ] Implement file upload
- [ ] Implement vote extraction
- [ ] Handle loading/error states

#### 3.3 Features
- [ ] Extraction history
- [ ] Download results (JSON, CSV)
- [ ] Real-time extraction progress

### Phase 4: Content Creator Integration (Week 4)

#### 4.1 Content Creator Pages
- [ ] Main content page (`/content`)
- [ ] Blog post generator (`/content/blog`)
- [ ] Video script generator (`/content/video`)
- [ ] Social media generator (`/content/social`)

#### 4.2 API Integration
- [ ] Create Content Creator API client
- [ ] Implement file uploads
- [ ] Implement content generation
- [ ] Handle multimodal inputs

#### 4.3 Content Editor
- [ ] Markdown editor for blog posts
- [ ] Rich text editor
- [ ] Preview mode
- [ ] Export options (MD, HTML, PDF)

### Phase 5: Advanced Features (Week 5)

#### 5.1 User Experience
- [ ] Loading skeletons
- [ ] Toast notifications
- [ ] Keyboard shortcuts
- [ ] Dark mode support

#### 5.2 Performance
- [ ] Image optimization
- [ ] Code splitting
- [ ] Server-side rendering
- [ ] Caching strategies

#### 5.3 Error Handling
- [ ] Global error boundary
- [ ] API error handling
- [ ] Retry logic
- [ ] Fallback UI

### Phase 6: Testing & Quality (Week 6)

#### 6.1 Testing
- [ ] Unit tests (Vitest)
- [ ] Component tests (React Testing Library)
- [ ] E2E tests (Playwright)
- [ ] API integration tests

#### 6.2 Code Quality
- [ ] ESLint configuration
- [ ] Prettier setup
- [ ] Type checking (TypeScript strict mode)
- [ ] Pre-commit hooks

### Phase 7: Deployment (Week 7)

#### 7.1 Docker Configuration
- [ ] Create Dockerfile for Next.js
- [ ] Multi-stage build optimization
- [ ] Environment variable management

#### 7.2 Cloud Run Deployment
- [ ] Deploy to Cloud Run
- [ ] Configure custom domain
- [ ] Set up HTTPS
- [ ] Configure CORS

#### 7.3 CI/CD
- [ ] GitHub Actions workflow
- [ ] Automated testing
- [ ] Automated deployment
- [ ] Rollback strategy

---

## 🔧 Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | Next.js 14 | React framework with SSR |
| **Language** | TypeScript | Type safety |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Components** | shadcn/ui | Accessible UI components |
| **Icons** | Lucide React | Modern icon library |
| **State** | Zustand | Lightweight state management |
| **Data Fetching** | TanStack Query | Server state management |
| **Forms** | React Hook Form | Form handling |
| **Validation** | Zod | Schema validation |
| **Testing** | Vitest + Playwright | Unit & E2E testing |
| **Deployment** | Docker + Cloud Run | Containerized deployment |

---

## 🌐 Environment Variables

```bash
# .env.local (development)
NEXT_PUBLIC_VOTE_API_URL=http://localhost:8000
NEXT_PUBLIC_CONTENT_API_URL=http://localhost:8002
NEXT_PUBLIC_APP_ENV=development

# .env.production
NEXT_PUBLIC_VOTE_API_URL=https://vote-extractor-xxx.run.app
NEXT_PUBLIC_CONTENT_API_URL=https://content-creator-xxx.run.app
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_DATADOG_RUM_APP_ID=xxx
NEXT_PUBLIC_DATADOG_RUM_CLIENT_TOKEN=xxx
```

---

## 📦 Docker Configuration

```dockerfile
# Dockerfile
FROM node:20-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

---

## 🚀 Getting Started

### Local Development

```bash
# Navigate to Next.js app
cd frontend/nextjs-web

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Build for Production

```bash
# Build
npm run build

# Start production server
npm start
```

### Docker Build

```bash
# Build image
docker build -t nextjs-frontend .

# Run container
docker run -p 3000:3000 nextjs-frontend
```

---

## 📊 Success Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| **Page Load Time** | < 2s | First contentful paint |
| **Time to Interactive** | < 3s | Fully interactive |
| **Lighthouse Score** | > 90 | Performance, accessibility |
| **Core Web Vitals** | All green | LCP, FID, CLS |
| **Bundle Size** | < 500KB | Initial JS bundle |

---

## 🎯 Key Features

### Sidebar Navigation
- ✅ Collapsible/expandable
- ✅ Active state indicators
- ✅ Icons + descriptions
- ✅ Mobile responsive
- ✅ "Add New Service" button

### Dashboard
- ✅ Service overview cards
- ✅ Recent activity
- ✅ Quick actions
- ✅ Usage statistics

### Responsive Design
- ✅ Desktop (1920px+)
- ✅ Laptop (1280px)
- ✅ Tablet (768px)
- ✅ Mobile (375px)

### Accessibility
- ✅ WCAG 2.1 AA compliant
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Focus indicators

---

## 🔗 Integration Points

### Vote Extractor API
- `POST /api/v1/extract/votes` - Extract votes from PDFs
- `GET /api/v1/models` - List available models
- `GET /health` - Health check

### Content Creator API
- `POST /api/v1/upload/file` - Upload media files
- `POST /api/v1/generate/blog-post` - Generate blog post
- `POST /api/v1/generate/video-script` - Generate video script
- `POST /api/v1/generate/social-media` - Generate social posts

---

## 📝 Next Steps

1. ✅ Update implementation plan
2. ⏳ Create Next.js project structure
3. ⏳ Implement Datadog theme
4. ⏳ Build sidebar navigation
5. ⏳ Create dashboard page
6. ⏳ Integrate with Vote Extractor API
7. ⏳ Integrate with Content Creator API
8. ⏳ Deploy to Cloud Run

---

**Status**: 📋 **Plan Complete - Ready for Implementation**

**Timeline**: 7 weeks (can be accelerated)

**Priority**: Phase 1-3 (Foundation + Vote Extractor) = MVP

