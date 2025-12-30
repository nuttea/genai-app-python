/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // Strict mode for React
  reactStrictMode: true,
  
  // API Proxy for Cloud Run backends
  async rewrites() {
    return [
      {
        source: '/api/vote-extractor/:path*',
        destination: `${process.env.VOTE_EXTRACTOR_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
      {
        source: '/api/content-creator/:path*',
        destination: `${process.env.CONTENT_CREATOR_API_URL || 'http://localhost:8002'}/api/v1/:path*`,
      },
    ];
  },
  
  // Image optimization
  images: {
    domains: ['storage.googleapis.com'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
      },
    ],
  },
  
  // Environment variables validation
  env: {
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'Datadog GenAI Platform',
    NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  },
  
  // Experimental features
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000'],
    },
  },
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;

