import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { APP_CONFIG } from '@/lib/constants/config';
import { FileText, Video, TrendingUp, CheckCircle } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Dashboard" />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {/* Welcome Section */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-foreground mb-2">
                Welcome to {APP_CONFIG.name}
              </h1>
              <p className="text-muted-foreground">
                Modern GenAI platform for creating content with AI-powered tools
              </p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatsCard
                title="Total Generations"
                value="0"
                icon={FileText}
                trend="+0%"
                color="purple"
              />
              <StatsCard
                title="Blog Posts"
                value="0"
                icon={FileText}
                trend="+0%"
                color="blue"
              />
              <StatsCard
                title="Video Scripts"
                value="0"
                icon={Video}
                trend="+0%"
                color="green"
              />
              <StatsCard
                title="Success Rate"
                value="100%"
                icon={CheckCircle}
                trend="+0%"
                color="orange"
              />
            </div>

            {/* Quick Start */}
            <div className="bg-card border border-border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Quick Start</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <QuickActionCard
                  title="Vote Extractor"
                  description="Extract vote data from Thai election documents"
                  href="/vote-extractor"
                  icon={FileText}
                />
                <QuickActionCard
                  title="Content Creator"
                  description="Generate blog posts, video scripts, and social media content"
                  href="/content-creator"
                  icon={Video}
                />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

function StatsCard({
  title,
  value,
  icon: Icon,
  trend,
  color,
}: {
  title: string;
  value: string;
  icon: any;
  trend: string;
  color: 'purple' | 'blue' | 'green' | 'orange';
}) {
  const colorClasses = {
    purple: 'bg-purple-100 text-purple-600',
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <span className="text-sm text-success font-medium">{trend}</span>
      </div>
      <h3 className="text-2xl font-bold text-foreground mb-1">{value}</h3>
      <p className="text-sm text-muted-foreground">{title}</p>
    </div>
  );
}

function QuickActionCard({
  title,
  description,
  href,
  icon: Icon,
}: {
  title: string;
  description: string;
  href: string;
  icon: any;
}) {
  return (
    <a
      href={href}
      className="block p-6 bg-card border border-border rounded-lg hover:border-purple-500 hover:shadow-lg transition-all duration-200 group"
    >
      <div className="flex items-start space-x-4">
        <div className="p-3 bg-purple-100 text-purple-600 rounded-lg group-hover:bg-purple-500 group-hover:text-white transition-colors">
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-foreground mb-1 group-hover:text-purple-600">
            {title}
          </h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
    </a>
  );
}

