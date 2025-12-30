/**
 * Application configuration constants
 */

export const APP_CONFIG = {
  name: process.env.NEXT_PUBLIC_APP_NAME || 'Datadog GenAI Platform',
  version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  description: 'Modern GenAI application platform for Datadog services',
} as const;

export const API_CONFIG = {
  voteExtractor: {
    baseUrl: process.env.NEXT_PUBLIC_VOTE_EXTRACTOR_API_URL || 'http://localhost:8000',
    timeout: 60000, // 60 seconds
  },
  contentCreator: {
    baseUrl: process.env.NEXT_PUBLIC_CONTENT_CREATOR_API_URL || 'http://localhost:8002',
    timeout: 120000, // 120 seconds for LLM operations
  },
} as const;

export const DATADOG_CONFIG = {
  applicationId: process.env.NEXT_PUBLIC_DD_APPLICATION_ID || '',
  clientToken: process.env.NEXT_PUBLIC_DD_CLIENT_TOKEN || '',
  site: process.env.NEXT_PUBLIC_DD_SITE || 'datadoghq.com',
  service: process.env.NEXT_PUBLIC_DD_SERVICE || 'nextjs-frontend',
  env: process.env.NEXT_PUBLIC_DD_ENV || 'development',
  version: process.env.NEXT_PUBLIC_DD_VERSION || '1.0.0',
  sessionReplayEnabled: process.env.NEXT_PUBLIC_DD_SESSION_REPLAY_ENABLED === 'true',
  sessionSampleRate: parseInt(process.env.NEXT_PUBLIC_DD_SESSION_SAMPLE_RATE || '100', 10),
  traceEnabled: process.env.NEXT_PUBLIC_DD_TRACE_ENABLED === 'true',
  traceSampleRate: parseInt(process.env.NEXT_PUBLIC_DD_TRACE_SAMPLE_RATE || '100', 10),
} as const;

export const ROUTES = {
  home: '/',
  voteExtractor: '/vote-extractor',
  contentCreator: {
    home: '/content-creator',
    interactive: '/content-creator/interactive',
    blogPost: '/content-creator/blog-post',
    videoScript: '/content-creator/video-script',
    socialMedia: '/content-creator/social-media',
  },
} as const;

export const FILE_UPLOAD = {
  maxSizeMB: 500,
  acceptedImageTypes: ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'],
  acceptedVideoTypes: ['video/mp4', 'video/mov', 'video/avi', 'video/webm'],
  acceptedDocTypes: ['application/pdf', 'text/plain', 'text/markdown'],
} as const;
