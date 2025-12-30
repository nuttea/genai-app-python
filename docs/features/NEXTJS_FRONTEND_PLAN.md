# 🎨 Next.js Frontend - Modern UI for GenAI Services

## Overview

A new **Next.js frontend application** that provides a modern, unified interface for all GenAI services in the platform. This is a separate service from the existing Streamlit frontend, designed for production use with Datadog branding and extensible architecture.

**Key Features**:
- ✨ Modern, responsive UI with Datadog color theme
- 🎯 Sidebar navigation for multiple GenAI services
- 🔌 Routes to Cloud Run backend APIs
- 📱 Mobile-friendly design
- 🚀 Server-side rendering (SSR) with Next.js
- 🎨 Component-based architecture for easy extension

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js Frontend (Port 3000)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐     │
│  │                 Sidebar Navigation                      │     │
│  │  - 🏠 Home / Dashboard                                 │     │
│  │  - 🗳️  Vote Extractor (existing)                       │     │
│  │  - 📝 Content Creator (new)                            │     │
│  │  - 🤖 [Future GenAI Services]                          │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              Main Content Area                         │     │
│  │  - Dynamic routing based on selected service          │     │
│  │  - File uploads                                        │     │
│  │  - Real-time generation status                         │     │
│  │  - Content preview and download                        │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       │ HTTP/2 (Cloud Run)
                       ▼
    ┌──────────────────────────────────────────────────┐
    │           Backend Services (Cloud Run)            │
    ├──────────────────────────────────────────────────┤
    │  • Vote Extractor API (Port 8000)                │
    │  • Content Creator API (Port 8002)               │
    │  • [Future Services]                             │
    └──────────────────────────────────────────────────┘
```

---

## 🎨 Datadog Design System

### Color Palette

```typescript
// Primary Datadog Colors
export const colors = {
  // Purple (Primary Brand)
  purple: {
    50: '#F5F3FF',
    100: '#EDE9FE',
    200: '#DDD6FE',
    300: '#C4B5FD',
    400: '#A78BFA',
    500: '#774AA4',  // Datadog Purple
    600: '#632D91',
    700: '#4F217A',
    800: '#3B1663',
    900: '#270B4C',
  },
  
  // Accent Colors
  green: '#27AE60',    // Success
  orange: '#F39C12',   // Warning
  red: '#E74C3C',      // Error
  blue: '#3498DB',     // Info
  
  // Neutrals
  gray: {
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
  
  // Background
  background: '#FAFAFA',
  surface: '#FFFFFF',
  border: '#E5E7EB',
};
```

### Typography

```typescript
// Fonts
export const fonts = {
  sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
  mono: "'Fira Code', 'Courier New', monospace",
};

// Font Sizes
export const fontSize = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem',  // 36px
};
```

---

## 📁 Project Structure

```
frontend/nextjs/
├── app/                          # Next.js 14 App Router
│   ├── layout.tsx               # Root layout with sidebar
│   ├── page.tsx                 # Home / Dashboard page
│   ├── vote-extractor/          # Vote Extractor service
│   │   └── page.tsx
│   ├── content-creator/         # Content Creator service
│   │   ├── page.tsx             # Main page
│   │   ├── blog-post/           # Blog post generation
│   │   ├── video-script/        # Video script generation
│   │   └── social-media/        # Social media posts
│   └── api/                     # API routes (proxy to Cloud Run)
│       ├── vote-extractor/
│       └── content-creator/
│
├── components/                   # React components
│   ├── layout/
│   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   ├── Header.tsx           # Top header
│   │   └── Footer.tsx           # Footer
│   ├── ui/                      # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── FileUpload.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── Toast.tsx
│   ├── services/                # Service-specific components
│   │   ├── VoteExtractor/
│   │   └── ContentCreator/
│   └── shared/                  # Shared components
│       ├── CodeBlock.tsx
│       └── MarkdownPreview.tsx
│
├── lib/                         # Utilities and helpers
│   ├── api/                     # API client functions
│   │   ├── voteExtractor.ts
│   │   └── contentCreator.ts
│   ├── utils/                   # Helper functions
│   │   ├── formatting.ts
│   │   └── validation.ts
│   └── constants/               # Constants
│       ├── colors.ts
│       └── config.ts
│
├── styles/
│   ├── globals.css              # Global styles
│   └── datadog-theme.css        # Datadog theme
│
├── public/
│   ├── logo.svg                 # Datadog logo
│   └── icons/                   # Service icons
│
├── types/                       # TypeScript types
│   ├── api.ts
│   └── components.ts
│
├── hooks/                       # Custom React hooks
│   ├── useApi.ts
│   └── useToast.ts
│
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS config
├── tsconfig.json                # TypeScript config
├── package.json
├── Dockerfile                   # Docker for local dev
├── Dockerfile.cloudrun          # Docker for Cloud Run
└── README.md
```

---

## 🎯 Implementation Phases

### Phase 1: Project Setup (Week 1)

#### ✅ Tasks
- [ ] Initialize Next.js 14 project with TypeScript
- [ ] Set up Tailwind CSS with Datadog theme
- [ ] Configure ESLint, Prettier
- [ ] Set up shadcn/ui components
- [ ] Create Docker setup
- [ ] Configure environment variables

```bash
# Initialize project
npx create-next-app@latest frontend/nextjs \
  --typescript \
  --tailwind \
  --app \
  --src-dir

# Install dependencies
cd frontend/nextjs
npm install @radix-ui/react-* class-variance-authority clsx tailwind-merge
npm install axios swr react-hot-toast lucide-react
npm install -D @types/node
```

#### Files to Create
1. `next.config.js` - API proxy to Cloud Run
2. `tailwind.config.js` - Datadog theme
3. `lib/constants/colors.ts` - Color palette
4. `app/layout.tsx` - Root layout
5. `Dockerfile` - Local development
6. `Dockerfile.cloudrun` - Production build

---

### Phase 2: Core UI Components (Week 1-2)

#### ✅ Sidebar Navigation

```typescript
// components/layout/Sidebar.tsx
import { Home, FileText, Video, Users, Settings } from 'lucide-react';

const services = [
  { name: 'Dashboard', icon: Home, href: '/' },
  { name: 'Vote Extractor', icon: FileText, href: '/vote-extractor' },
  { name: 'Content Creator', icon: Video, href: '/content-creator' },
  // Add more services here
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-purple-600 text-white">
      <div className="p-6">
        <img src="/logo.svg" alt="Datadog" className="h-8" />
        <h1 className="mt-4 text-xl font-bold">GenAI Platform</h1>
      </div>
      
      <nav className="mt-8">
        {services.map((service) => (
          <Link key={service.name} href={service.href}>
            <div className="flex items-center px-6 py-3 hover:bg-purple-700">
              <service.icon className="w-5 h-5 mr-3" />
              {service.name}
            </div>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

#### ✅ Reusable UI Components

Create using shadcn/ui:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add select
npx shadcn-ui@latest add toast
```

#### Files to Create
1. `components/layout/Sidebar.tsx`
2. `components/layout/Header.tsx`
3. `components/ui/*` (shadcn/ui components)
4. `components/shared/FileUpload.tsx`
5. `components/shared/LoadingSpinner.tsx`

---

### Phase 3: API Integration (Week 2)

#### ✅ API Client Setup

```typescript
// lib/api/contentCreator.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_CONTENT_CREATOR_API || 'http://localhost:8002';

export const contentCreatorApi = {
  // Upload file
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(`${API_BASE_URL}/api/v1/upload/file`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    return response.data;
  },
  
  // Generate blog post
  generateBlogPost: async (request: BlogPostRequest) => {
    const response = await axios.post(`${API_BASE_URL}/api/v1/generate/blog-post`, request);
    return response.data;
  },
  
  // Generate video script
  generateVideoScript: async (request: VideoScriptRequest) => {
    const response = await axios.post(`${API_BASE_URL}/api/v1/generate/video-script`, request);
    return response.data;
  },
  
  // Generate social media posts
  generateSocialMedia: async (request: SocialMediaRequest) => {
    const response = await axios.post(`${API_BASE_URL}/api/v1/generate/social-media`, request);
    return response.data;
  },
};
```

#### ✅ API Routes (Proxy)

```typescript
// app/api/content-creator/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.CONTENT_CREATOR_API_URL || 'http://localhost:8002';

export async function POST(request: NextRequest) {
  const path = request.nextUrl.pathname.replace('/api/content-creator/', '');
  const body = await request.json();
  
  const response = await fetch(`${API_BASE_URL}/api/v1/${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  
  const data = await response.json();
  return NextResponse.json(data);
}
```

#### Files to Create
1. `lib/api/voteExtractor.ts`
2. `lib/api/contentCreator.ts`
3. `app/api/content-creator/[...path]/route.ts`
4. `app/api/vote-extractor/[...path]/route.ts`
5. `hooks/useApi.ts`

---

### Phase 4: Content Creator Pages (Week 3)

#### ✅ Main Content Creator Page

```typescript
// app/content-creator/page.tsx
export default function ContentCreatorPage() {
  return (
    <div className="max-w-7xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Datadog Content Creator</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ServiceCard
          title="Blog Post"
          description="Generate professional blog posts"
          icon={FileText}
          href="/content-creator/blog-post"
        />
        
        <ServiceCard
          title="Video Script"
          description="Create 60s video scripts"
          icon={Video}
          href="/content-creator/video-script"
        />
        
        <ServiceCard
          title="Social Media"
          description="Generate platform-specific posts"
          icon={Share2}
          href="/content-creator/social-media"
        />
      </div>
    </div>
  );
}
```

#### ✅ Blog Post Generation Page

```typescript
// app/content-creator/blog-post/page.tsx
'use client';

import { useState } from 'react';
import { FileUpload } from '@/components/shared/FileUpload';
import { contentCreatorApi } from '@/lib/api/contentCreator';

export default function BlogPostPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [generatedPost, setGeneratedPost] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleGenerate = async () => {
    setLoading(true);
    try {
      const result = await contentCreatorApi.generateBlogPost({
        title,
        description,
        style: 'professional',
        target_audience: 'DevOps engineers',
      });
      setGeneratedPost(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Generate Blog Post</h1>
      
      <div className="space-y-6">
        <Input
          label="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter blog post title"
        />
        
        <Textarea
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what you want to write about..."
          rows={6}
        />
        
        <FileUpload
          accept="video/*,image/*"
          onUpload={(files) => console.log('Uploaded:', files)}
        />
        
        <Button
          onClick={handleGenerate}
          loading={loading}
          className="w-full"
        >
          Generate Blog Post
        </Button>
        
        {generatedPost && (
          <Card className="mt-8">
            <MarkdownPreview content={generatedPost.content} />
          </Card>
        )}
      </div>
    </div>
  );
}
```

#### Files to Create
1. `app/content-creator/page.tsx`
2. `app/content-creator/blog-post/page.tsx`
3. `app/content-creator/video-script/page.tsx`
4. `app/content-creator/social-media/page.tsx`
5. `components/services/ContentCreator/BlogPostForm.tsx`

---

### Phase 5: Dashboard & Analytics (Week 4)

#### ✅ Dashboard

```typescript
// app/page.tsx
export default function DashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">GenAI Platform Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="Total Generations"
          value="1,234"
          icon={FileText}
          trend="+12%"
        />
        
        <StatsCard
          title="Blog Posts"
          value="456"
          icon={FileText}
          trend="+8%"
        />
        
        <StatsCard
          title="Video Scripts"
          value="789"
          icon={Video}
          trend="+15%"
        />
        
        <StatsCard
          title="Success Rate"
          value="98.5%"
          icon={CheckCircle}
          trend="+2%"
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentGenerations />
        <PopularServices />
      </div>
    </div>
  );
}
```

#### Files to Create
1. `app/page.tsx` (Dashboard)
2. `components/dashboard/StatsCard.tsx`
3. `components/dashboard/RecentGenerations.tsx`
4. `components/dashboard/PopularServices.tsx`

---

### Phase 6: Deployment & CI/CD (Week 4)

#### ✅ Docker Configuration

```dockerfile
# Dockerfile.cloudrun
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build Next.js
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

#### ✅ GitHub Actions

```yaml
# .github/workflows/nextjs-frontend.yml
name: Next.js Frontend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'frontend/nextjs/**'
  pull_request:
    paths:
      - 'frontend/nextjs/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/nextjs/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend/nextjs
        run: npm ci
      
      - name: Lint
        working-directory: frontend/nextjs
        run: npm run lint
      
      - name: Build
        working-directory: frontend/nextjs
        run: npm run build
      
      - name: Deploy to Cloud Run
        if: github.ref == 'refs/heads/main'
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: nextjs-frontend
          region: us-central1
          source: ./frontend/nextjs
```

#### Files to Create
1. `Dockerfile`
2. `Dockerfile.cloudrun`
3. `.github/workflows/nextjs-frontend.yml`
4. `next.config.js` (API rewrites)
5. `.env.example`

---

## 🎨 UI/UX Features

### Sidebar Navigation
- **Collapsible**: Can collapse to icons only
- **Active state**: Highlights current service
- **Keyboard shortcuts**: Quick navigation
- **Search**: Find services quickly

### File Upload
- **Drag and drop**: Easy file uploads
- **Multi-file**: Upload multiple files
- **Progress**: Real-time upload progress
- **Preview**: Show thumbnails for images/videos

### Content Generation
- **Real-time status**: Show generation progress
- **Live preview**: See content as it generates
- **Edit mode**: Edit generated content
- **Export options**: Download in multiple formats

### Responsive Design
- **Mobile**: Touch-friendly interface
- **Tablet**: Optimized for iPad
- **Desktop**: Full features with sidebar

---

## 🔧 Configuration

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_APP_NAME="Datadog GenAI Platform"
NEXT_PUBLIC_APP_VERSION="1.0.0"

# API URLs (Cloud Run)
NEXT_PUBLIC_VOTE_EXTRACTOR_API=https://vote-extractor-xxx.run.app
NEXT_PUBLIC_CONTENT_CREATOR_API=https://content-creator-xxx.run.app

# Server-side API URLs (internal)
VOTE_EXTRACTOR_API_URL=http://vote-extractor:8000
CONTENT_CREATOR_API_URL=http://content-creator:8002

# Datadog RUM
NEXT_PUBLIC_DD_APPLICATION_ID=your-app-id
NEXT_PUBLIC_DD_CLIENT_TOKEN=your-client-token
NEXT_PUBLIC_DD_SITE=datadoghq.com
NEXT_PUBLIC_DD_SERVICE=nextjs-frontend
NEXT_PUBLIC_DD_ENV=production
```

### Next.js Config

```javascript
// next.config.js
module.exports = {
  output: 'standalone',
  
  // API Proxy
  async rewrites() {
    return [
      {
        source: '/api/vote-extractor/:path*',
        destination: `${process.env.VOTE_EXTRACTOR_API_URL}/api/:path*`,
      },
      {
        source: '/api/content-creator/:path*',
        destination: `${process.env.CONTENT_CREATOR_API_URL}/api/v1/:path*`,
      },
    ];
  },
  
  // Image optimization
  images: {
    domains: ['storage.googleapis.com'],
  },
};
```

---

## 📊 Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | Next.js 14 | React framework with SSR |
| **Language** | TypeScript | Type safety |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **UI Components** | shadcn/ui | Accessible components |
| **Icons** | Lucide React | Modern icons |
| **HTTP Client** | Axios | API requests |
| **State Management** | SWR | Data fetching |
| **Forms** | React Hook Form | Form handling |
| **Validation** | Zod | Schema validation |
| **Toast Notifications** | react-hot-toast | User feedback |
| **Code Highlighting** | Prism.js | Syntax highlighting |
| **Markdown** | react-markdown | Markdown preview |

---

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
cd frontend/nextjs
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  nextjs-frontend:
    build:
      context: ./frontend/nextjs
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VOTE_EXTRACTOR_API_URL=http://fastapi-backend:8000
      - CONTENT_CREATOR_API_URL=http://content-creator:8002
    depends_on:
      - fastapi-backend
      - content-creator
```

### Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy nextjs-frontend \
  --source ./frontend/nextjs \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars VOTE_EXTRACTOR_API_URL=https://vote-extractor-xxx.run.app,CONTENT_CREATOR_API_URL=https://content-creator-xxx.run.app
```

---

## 📈 Future Enhancements

### Phase 7: Advanced Features
- [ ] User authentication (Firebase Auth)
- [ ] Usage analytics dashboard
- [ ] Generation history
- [ ] Favorites/bookmarks
- [ ] Team collaboration
- [ ] API key management

### Phase 8: Performance
- [ ] Edge caching with Vercel/Cloudflare
- [ ] Image optimization
- [ ] Code splitting
- [ ] Lazy loading

### Phase 9: Additional Services
- [ ] Document analyzer
- [ ] Image generator
- [ ] Code assistant
- [ ] Translation service

---

## 📝 Implementation Checklist

### Week 1: Setup
- [ ] Initialize Next.js project
- [ ] Configure Tailwind with Datadog theme
- [ ] Set up shadcn/ui components
- [ ] Create sidebar navigation
- [ ] Implement basic layout

### Week 2: API Integration
- [ ] Create API client functions
- [ ] Set up API routes (proxy)
- [ ] Implement file upload
- [ ] Add error handling

### Week 3: Content Creator UI
- [ ] Blog post generation page
- [ ] Video script generation page
- [ ] Social media posts page
- [ ] Content preview components

### Week 4: Dashboard & Deployment
- [ ] Build dashboard
- [ ] Add analytics
- [ ] Configure Docker
- [ ] Set up CI/CD
- [ ] Deploy to Cloud Run

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| **Page Load Time** | < 2s |
| **Time to Interactive** | < 3s |
| **Lighthouse Score** | > 90 |
| **Mobile Responsive** | 100% |
| **API Response Time** | < 500ms |
| **User Satisfaction** | > 4.5/5 |

---

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Datadog Design System](https://www.datadoghq.com/design-system/)
- [Lucide Icons](https://lucide.dev/)

---

**Status**: 📝 **Plan Complete - Ready for Implementation**

**Timeline**: 4 weeks

**Team**: 1-2 frontend developers

**Dependencies**: Backend APIs (Vote Extractor, Content Creator)

