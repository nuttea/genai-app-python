import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { FileText, Video, Share2, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { ROUTES } from '@/lib/constants/config';

export default function ContentCreatorPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Content Creator" />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {/* Hero Section */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-foreground mb-2">
                Datadog Content Creator
              </h1>
              <p className="text-muted-foreground text-lg">
                Generate high-quality blog posts, video scripts, and social media content about
                Datadog products using AI
              </p>
            </div>

            {/* Interactive Mode Banner */}
            <Link
              href={ROUTES.contentCreator.interactive}
              className="block mb-6 p-6 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg text-white hover:shadow-lg transition-all duration-200 group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Sparkles className="w-6 h-6" />
                    <h2 className="text-2xl font-bold">🆕 Interactive Mode (Recommended)</h2>
                  </div>
                  <p className="text-purple-100 mb-2">
                    Chat with our AI agent that guides you through the complete content creation workflow
                  </p>
                  <ul className="space-y-1 text-sm text-purple-100">
                    <li>✨ Multi-agent collaboration with auto-validation</li>
                    <li>🔄 Interactive feedback loops for refinement</li>
                    <li>📁 File upload and analysis support</li>
                    <li>⚡ Real-time streaming responses</li>
                  </ul>
                </div>
                <div className="text-white group-hover:translate-x-2 transition-transform">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </Link>

            {/* Service Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ServiceCard
                title="Blog Post"
                description="Generate professional blog posts with AI-powered content creation"
                icon={FileText}
                href={ROUTES.contentCreator.blogPost}
                color="purple"
                features={[
                  'AI-powered writing',
                  'SEO optimized',
                  'Multiple formats',
                  'Image analysis support',
                ]}
              />

              <ServiceCard
                title="Video Script"
                description="Create engaging 60-second video scripts for YouTube Shorts, TikTok, and Reels"
                icon={Video}
                href={ROUTES.contentCreator.videoScript}
                color="blue"
                features={[
                  '60-second format',
                  'Scene breakdown',
                  'Platform optimized',
                  'Video input support',
                ]}
              />

              <ServiceCard
                title="Social Media"
                description="Generate platform-specific posts for LinkedIn, Twitter, and Instagram"
                icon={Share2}
                href={ROUTES.contentCreator.socialMedia}
                color="green"
                features={[
                  'Multi-platform',
                  'Hashtag suggestions',
                  'Character limits',
                  'Engagement focused',
                ]}
              />
            </div>

            {/* Features Section */}
            <div className="mt-12 bg-card border border-border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Key Features</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FeatureItem
                  title="Multimodal Input"
                  description="Upload text, markdown, images, or videos as input for content generation"
                />
                <FeatureItem
                  title="Gemini 2.5 Flash"
                  description="Powered by Google's latest Gemini AI model for high-quality output"
                />
                <FeatureItem
                  title="Datadog Focused"
                  description="Specialized in creating content about Datadog products and features"
                />
                <FeatureItem
                  title="Export Options"
                  description="Download generated content in multiple formats (Markdown, HTML, JSON)"
                />
              </div>
            </div>

            {/* Getting Started */}
            <div className="mt-8 bg-purple-50 border border-purple-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-purple-900 mb-2">
                🚀 Getting Started
              </h3>
              <ol className="list-decimal list-inside space-y-2 text-purple-800">
                <li>Choose a content type above (Blog Post, Video Script, or Social Media)</li>
                <li>Provide your topic or upload reference materials</li>
                <li>Customize generation settings (optional)</li>
                <li>Generate and review your AI-created content</li>
                <li>Export or share your content</li>
              </ol>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

interface ServiceCardProps {
  title: string;
  description: string;
  icon: any;
  href: string;
  color: 'purple' | 'blue' | 'green';
  features: string[];
}

function ServiceCard({ title, description, icon: Icon, href, color, features }: ServiceCardProps) {
  const colorClasses = {
    purple: 'bg-purple-100 text-purple-600 group-hover:bg-purple-600',
    blue: 'bg-blue-100 text-blue-600 group-hover:bg-blue-600',
    green: 'bg-green-100 text-green-600 group-hover:bg-green-600',
  };

  const borderClasses = {
    purple: 'hover:border-purple-500',
    blue: 'hover:border-blue-500',
    green: 'hover:border-green-500',
  };

  return (
    <Link
      href={href}
      className={`block p-6 bg-card border border-border rounded-lg ${borderClasses[color]} hover:shadow-lg transition-all duration-200 group`}
    >
      <div className="flex items-start space-x-4 mb-4">
        <div
          className={`p-3 rounded-lg ${colorClasses[color]} group-hover:text-white transition-colors`}
        >
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-foreground mb-1 group-hover:text-purple-600">
            {title}
          </h3>
        </div>
      </div>
      <p className="text-sm text-muted-foreground mb-4">{description}</p>
      <ul className="space-y-2">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center text-sm text-muted-foreground">
            <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2" />
            {feature}
          </li>
        ))}
      </ul>
    </Link>
  );
}

interface FeatureItemProps {
  title: string;
  description: string;
}

function FeatureItem({ title, description }: FeatureItemProps) {
  return (
    <div className="flex items-start space-x-3">
      <div className="w-2 h-2 bg-purple-500 rounded-full mt-2" />
      <div>
        <h4 className="font-medium text-foreground">{title}</h4>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}

