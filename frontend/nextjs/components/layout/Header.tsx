'use client';

import { Bell, Settings } from 'lucide-react';
import { UserProfile } from '@/components/auth/UserProfile';

interface HeaderProps {
  title: string;
}

export function Header({ title }: HeaderProps) {
  return (
    <header className="h-16 border-b border-border bg-surface px-6 flex items-center justify-between">
      <div className="flex-1">
        <h2 className="text-2xl font-semibold text-foreground">{title}</h2>
      </div>

      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <button
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
        </button>

        {/* Settings */}
        <button
          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
          aria-label="Settings"
        >
          <Settings className="w-5 h-5" />
        </button>

        {/* User Profile - Compact Mode */}
        <div className="pl-4 border-l border-border">
          <UserProfile compact={true} />
        </div>
      </div>
    </header>
  );
}
