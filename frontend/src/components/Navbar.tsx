import React from 'react';
import {
  LayoutDashboard,
  GitFork,
  Database,
  PlayCircle,
  Eye,
} from 'lucide-react';
import { HealthStatus } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: HealthStatus | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, health }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'workflow', label: 'Agent Workflow', icon: GitFork },
    { id: 'memory', label: 'Memory Explorer', icon: Database },
    { id: 'executions', label: 'Playground', icon: PlayCircle },
    { id: 'inspector', label: 'Memory Inspector', icon: Eye },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-[#E6E8EC] h-14">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between gap-4">
        {/* Left: Brand & Product Name */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-7 h-7 rounded-md bg-[#20242C] flex items-center justify-center text-white shadow-xs">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm text-[#20242C] tracking-tight">ContextCraft</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#F2F4F7] text-[#667085] border border-[#E4E7EC]">
              v1.0 MVP
            </span>
          </div>
        </div>

        {/* Center: Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-[#F2F4F7] text-[#20242C] font-semibold'
                    : 'text-[#667085] hover:text-[#20242C] hover:bg-[#F8F9FB]'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#5558D9]' : 'text-[#98A2B3]'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Mobile Navigation Dropdown/Scroll */}
        <div className="flex md:hidden items-center gap-1 overflow-x-auto py-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`px-2.5 py-1 text-xs font-medium rounded whitespace-nowrap ${
                  isActive ? 'bg-[#F2F4F7] text-[#20242C]' : 'text-[#667085]'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>

        {/* Right: Mode & Health Indicators */}
        <div className="flex items-center gap-2.5 shrink-0">
          {health?.mock_mode ? (
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium rounded bg-[#F8F9FB] text-[#667085] border border-[#E6E8EC]">
              Mock Mode
            </span>
          ) : (
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium rounded bg-[#EEF0FD] text-[#5558D9] border border-[#D6DAFB]">
              Live LLM
            </span>
          )}

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white border border-[#E6E8EC] text-[11px] text-[#667085]">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                health?.status === 'healthy' ? 'bg-[#15966B]' : 'bg-[#D84A5B]'
              }`}
            />
            <span className="hidden sm:inline">
              {health?.status === 'healthy' ? 'Operational' : 'Connecting'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
