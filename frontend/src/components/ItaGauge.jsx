import React from 'react';

export default function ItaGauge({ ita = 34.2, band = "intermediate" }) {
  const clampedIta = Math.max(-30, Math.min(70, ita));
  const angle = ((clampedIta + 30) / 100) * 180;

  const bandColors = {
    very_light: "#F9ECE6",
    light: "#F3D5C8",
    intermediate: "#DCA78E",
    tan: "#B97F63",
    brown: "#8A5438",
    dark: "#4E2B1A"
  };

  return (
    <div class="flex flex-col items-center justify-center p-6 app-surface border app-border rounded-2xl shadow-sm space-y-3">
      <div class="relative w-48 h-24">
        <svg viewBox="0 0 100 50" class="w-full h-full">
          <path
            d="M 10 50 A 40 40 0 0 1 90 50"
            fill="none"
            stroke="var(--surface-alt)"
            strokeWidth="10"
            strokeLinecap="round"
          />

          <path d="M 10 50 A 40 40 0 0 1 18 28" fill="none" stroke="#4E2B1A" strokeWidth="10" />
          <path d="M 18 28 A 40 40 0 0 1 32 15" fill="none" stroke="#8A5438" strokeWidth="10" />
          <path d="M 32 15 A 40 40 0 0 1 50 10" fill="none" stroke="#B97F63" strokeWidth="10" />
          <path d="M 50 10 A 40 40 0 0 1 68 15" fill="none" stroke="#DCA78E" strokeWidth="10" />
          <path d="M 68 15 A 40 40 0 0 1 82 28" fill="none" stroke="#F3D5C8" strokeWidth="10" />
          <path d="M 82 28 A 40 40 0 0 1 90 50" fill="none" stroke="#F9ECE6" strokeWidth="10" />

          <circle cx="50" cy="50" r="4" fill="var(--text)" />
          
          <line
            x1="50"
            y1="50"
            x2="50"
            y2="16"
            stroke="var(--text)"
            strokeWidth="2.5"
            strokeLinecap="round"
            style={{
              transformOrigin: "50px 50px",
              transform: `rotate(${angle - 90}deg)`,
              transition: "transform 800ms cubic-bezier(.4, 0, .2, 1)"
            }}
          />
        </svg>
      </div>

      <div class="text-center space-y-1">
        <div class="text-2xl font-extrabold app-text tabular-nums">
          {ita.toFixed(1)}°
        </div>
        <div class="inline-block px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full text-white shadow-xs" style={{ backgroundColor: bandColors[band] || "#DCA78E" }}>
          {band.replace('_', ' ')}
        </div>
      </div>
    </div>
  );
}
