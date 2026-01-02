'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, FileText, Video, Menu, X, Image as ImageIcon } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { APP_CONFIG, ROUTES } from '@/lib/constants/config';

const services = [
  { name: 'Dashboard', icon: Home, href: ROUTES.home },
  { name: 'Vote Extractor', icon: FileText, href: ROUTES.voteExtractor },
  { name: 'Content Creator', icon: Video, href: ROUTES.contentCreator.home },
  { name: 'Image Creator', icon: ImageIcon, href: ROUTES.imageCreator.home },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="fixed top-4 left-4 z-50 p-2 bg-purple-600 text-white rounded-lg lg:hidden"
        aria-label="Toggle menu"
      >
        {isMobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Overlay for mobile */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed lg:static inset-y-0 left-0 z-40 w-64 bg-datadog-gradient text-white transform transition-transform duration-300 ease-in-out',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo Section */}
          <div className="p-6 border-b border-purple-700">
            <h1 className="text-xl font-bold">{APP_CONFIG.name}</h1>
            <p className="text-xs text-purple-200 mt-1">v{APP_CONFIG.version}</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-6 space-y-1 overflow-y-auto scrollbar-thin">
            {services.map((service) => {
              const isActive =
                pathname === service.href ||
                (service.href !== ROUTES.home && pathname.startsWith(service.href));

              return (
                <Link
                  key={service.name}
                  href={service.href}
                  onClick={() => setIsMobileOpen(false)}
                  className={cn(
                    'flex items-center px-4 py-3 rounded-lg transition-all duration-200',
                    isActive
                      ? 'bg-white/20 text-white font-medium'
                      : 'text-purple-100 hover:bg-white/10 hover:text-white'
                  )}
                >
                  <service.icon className="w-5 h-5 mr-3" />
                  <span>{service.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-6 border-t border-purple-700">
            <p className="text-xs text-purple-200">© 2024 Datadog. All rights reserved.</p>
          </div>
        </div>
      </aside>
    </>
  );
}
