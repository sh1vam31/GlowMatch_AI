import React from 'react';
import { Sparkles, Compass, Camera, Calendar, ExternalLink, Sun, Moon } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, theme, toggleTheme }) {
  return (
    <header class="sticky top-0 z-50 app-surface/85 backdrop-blur-md border-b app-border transition-all">
      <div class="max-w-[1180px] mx-auto px-6 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div class="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('discover')}>
          <div class="w-9 h-9 rounded-full bg-[var(--accent)] flex items-center justify-center text-white font-extrabold text-base shadow-sm">
            G
          </div>
          <div class="flex flex-col">
            <span class="font-extrabold text-lg tracking-tight app-text leading-none">
              GlowMatch <span class="text-[var(--accent)]">AI</span>
            </span>
            <span class="text-[10px] font-semibold app-text-muted tracking-wider uppercase mt-0.5">Beauty Engine</span>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav class="flex items-center space-x-1 app-surface-alt p-1 rounded-full border app-border shadow-inner">
          <button
            onClick={() => setActiveTab('discover')}
            class={`flex items-center space-x-1.5 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'discover'
                ? 'app-surface app-text shadow-sm'
                : 'app-text-muted hover:app-text'
            }`}
          >
            <Compass class="w-3.5 h-3.5 text-[var(--accent)]" />
            <span>Discover</span>
          </button>

          <button
            onClick={() => setActiveTab('analyze')}
            class={`flex items-center space-x-1.5 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'analyze'
                ? 'app-surface app-text shadow-sm'
                : 'app-text-muted hover:app-text'
            }`}
          >
            <Camera class="w-3.5 h-3.5 text-[var(--accent)]" />
            <span>Analyze Selfie</span>
          </button>

          <button
            onClick={() => setActiveTab('routine')}
            class={`flex items-center space-x-1.5 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'routine'
                ? 'app-surface app-text shadow-sm'
                : 'app-text-muted hover:app-text'
            }`}
          >
            <Calendar class="w-3.5 h-3.5 text-[var(--accent)]" />
            <span>Routine Builder</span>
          </button>
        </nav>

        {/* Action Links & Theme Toggle */}
        <div class="flex items-center space-x-2">
          <button
            onClick={toggleTheme}
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
            class="p-2 rounded-full border app-border app-surface app-text hover:text-[var(--accent)] transition shadow-sm flex items-center justify-center cursor-pointer"
          >
            {theme === 'light' ? (
              <Moon class="w-4 h-4 text-slate-700" />
            ) : (
              <Sun class="w-4 h-4 text-amber-400" />
            )}
          </button>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            class="flex items-center space-x-1 text-xs font-semibold app-text-muted hover:text-[var(--accent)] border app-border px-3.5 py-1.5 rounded-full app-surface transition hover:shadow-sm"
          >
            <span>API Specs</span>
            <ExternalLink class="w-3 h-3 ml-0.5 opacity-70" />
          </a>
        </div>
      </div>
    </header>
  );
}
