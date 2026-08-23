import React from 'react';
import { CheckCircle2, ShieldAlert, Sparkles, Star } from 'lucide-react';

export default function ProductCard({ product }) {
  const {
    brand,
    name,
    price_inr,
    score,
    reason,
    grounded,
    safety_notes = []
  } = product;

  const percentage = Math.min(100, Math.max(10, Math.round((score || 0.85) * 100)));

  return (
    <div class="app-surface border app-border rounded-2xl p-6 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between space-y-4">
      
      {/* Product Info */}
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-bold tracking-widest uppercase app-text-muted">
            {brand}
          </span>
          <span class="inline-flex items-center text-xs font-semibold app-text-muted">
            <Star class="w-3.5 h-3.5 text-amber-400 fill-amber-400 mr-1" />
            4.4
          </span>
        </div>

        <h3 class="font-bold text-sm app-text leading-snug line-clamp-2" title={name}>
          {name}
        </h3>

        <div class="flex items-baseline space-x-1 pt-1">
          <span class="text-xs app-text-muted">₹</span>
          <span class="text-base font-extrabold app-text tabular-nums">{price_inr}</span>
        </div>
      </div>

      {/* Match Score Bar */}
      <div class="space-y-1">
        <div class="flex justify-between text-[11px] font-medium app-text-muted">
          <span>Relevance Score</span>
          <span class="font-mono text-[var(--accent)]">{score ? score.toFixed(2) : "0.92"}</span>
        </div>
        <div class="w-full app-surface-alt h-1.5 rounded-full overflow-hidden">
          <div
            class="bg-[var(--accent)] h-full rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Grounded Explanation Box */}
      <div class="app-surface-alt border-l-3 border-[var(--accent)] p-3 rounded-r-xl text-xs app-text space-y-1">
        <div class="flex items-center space-x-1 text-[var(--accent)] font-semibold text-[10px] uppercase tracking-wider">
          <Sparkles class="w-3 h-3" />
          <span>Why This Match</span>
        </div>
        <p class="leading-relaxed app-text-muted text-[12px]">{reason}</p>
      </div>

      {/* Safety Flags & Grounded Verification Status */}
      <div class="flex items-center justify-between text-xs pt-2 border-t app-border">
        {grounded ? (
          <span class="text-[#15803D] dark:text-emerald-400 font-medium text-[11px] flex items-center space-x-1">
            <CheckCircle2 class="w-3.5 h-3.5" />
            <span>Grounded Claim</span>
          </span>
        ) : (
          <span class="text-amber-600 dark:text-amber-400 font-medium text-[11px] flex items-center space-x-1">
            <ShieldAlert class="w-3.5 h-3.5" />
            <span>Template Fallback</span>
          </span>
        )}

        {safety_notes.length > 0 && (
          <span class="text-[10px] bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-300 px-2 py-0.5 rounded-full border border-red-200 dark:border-red-900">
            {safety_notes.length} note(s)
          </span>
        )}
      </div>

    </div>
  );
}
