'use client';

import { Bell, Settings, User } from 'lucide-react';

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

        {/* User Profile */}
        <button
          className="flex items-center space-x-2 p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
          aria-label="User menu"
        >
          <div className="w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center">
            <User className="w-4 h-4" />
          </div>
          <span className="text-sm font-medium hidden md:block">User</span>
        </button>
      </div>
    </header>
  );
}

