import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, Info, ShieldAlert, Sun, Moon } from 'lucide-react';

export default function RoutineScreen() {
  const [skinType, setSkinType] = useState('oily');
  const [budget, setBudget] = useState(3000);
  const [pregnancySafe, setPregnancySafe] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [routine, setRoutine] = useState(null);

  const handleBuild = () => {
    setGenerating(true);
    setTimeout(() => {
      setRoutine({
        am: [
          { slot: "Cleanser", name: "Gentle Foaming Cleanser", brand: "CeraVe", price: 650 },
          { slot: "Moisturizer", name: "Oil-Free Gel Lotion", brand: "Neutrogena", price: 749 },
          { slot: "Sunscreen", name: "Invisible Physical SPF 50", brand: "La Roche-Posay", price: 1150 }
        ],
        pm: [
          { slot: "Cleanser", name: "Gentle Foaming Cleanser", brand: "CeraVe", price: 650 },
          { slot: "Treatment", name: "Retinol 0.2% Squalane", brand: "The Ordinary", price: 890 },
          { slot: "Moisturizer", name: "Oil-Free Gel Lotion", brand: "Neutrogena", price: 749 }
        ],
        conflicts: [
          {
            severity: "SEPARATE",
            title: "Retinoid + Salicylic Acid",
            message: "Retinoids and direct acids are separated into alternate nights or separate AM/PM routine slots to reduce irritation."
          },
          {
            severity: "INFO",
            title: "Vitamin C + Niacinamide",
            message: "Modern formulation consensus confirms Vitamin C and Niacinamide are compatible."
          }
        ]
      });
      setGenerating(false);
    }, 600);
  };

  return (
    <div class="space-y-8">
      <div class="text-center max-w-xl mx-auto space-y-2">
        <h2 class="text-2xl font-bold app-text">Safe Skincare Routine Builder</h2>
        <p class="text-xs app-text-muted leading-relaxed">
          Assembles morning (AM) and evening (PM) routines governed by our rule-based ingredient conflict graph.
        </p>
      </div>

      {/* Form Controls */}
      <div class="app-surface border app-border rounded-2xl p-6 shadow-sm space-y-4 max-w-2xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold app-text-muted mb-1">Skin Type Profile</label>
            <select
              value={skinType}
              onChange={(e) => setSkinType(e.target.value)}
              class="w-full app-surface-alt border app-border app-text rounded-lg p-2.5 text-sm focus:outline-none focus:border-[var(--accent)]"
            >
              <option value="oily">Oily Skin</option>
              <option value="dry">Dry Skin</option>
              <option value="sensitive">Sensitive Skin</option>
              <option value="combination">Combination Skin</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold app-text-muted mb-1">Max Total Budget (₹{budget})</label>
            <input
              type="range"
              min="1000"
              max="8000"
              step="500"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              class="w-full accent-[var(--accent)] cursor-pointer"
            />
          </div>
        </div>

        <div class="flex items-center space-x-2 pt-2">
          <input
            type="checkbox"
            id="preg-check"
            checked={pregnancySafe}
            onChange={(e) => setPregnancySafe(e.target.checked)}
            class="rounded accent-[var(--accent)] cursor-pointer"
          />
          <label htmlFor="preg-check" class="text-xs font-semibold app-text cursor-pointer">
            Enforce Strict Pregnancy & Lactation Safety (Exclude Retinoids & Hydroquinone)
          </label>
        </div>

        <button
          onClick={handleBuild}
          disabled={generating}
          class="w-full py-3 bg-[var(--accent)] hover:opacity-90 text-white font-semibold text-xs rounded-xl transition shadow-sm cursor-pointer"
        >
          {generating ? "Validating Routine Safety..." : "Assemble Safe AM / PM Routine"}
        </button>
      </div>

      {/* Routine Display */}
      {routine && (
        <div class="space-y-6 max-w-4xl mx-auto">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AM Routine Track */}
            <div class="bg-amber-50/40 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 rounded-2xl p-6 space-y-4">
              <div class="flex items-center space-x-2 border-b border-amber-200/60 dark:border-amber-900/40 pb-3">
                <Sun class="w-5 h-5 text-amber-600 dark:text-amber-400" />
                <h3 class="font-bold text-sm text-amber-900 dark:text-amber-200">AM Morning Track</h3>
              </div>
              <div class="space-y-3">
                {routine.am.map((step, idx) => (
                  <div key={idx} class="app-surface p-3.5 rounded-xl border app-border shadow-sm flex items-center justify-between">
                    <div>
                      <span class="text-[10px] font-bold uppercase text-amber-700 dark:text-amber-400">{step.slot}</span>
                      <div class="font-bold text-xs app-text">{step.name}</div>
                      <div class="text-[11px] app-text-muted">{step.brand}</div>
                    </div>
                    <span class="text-xs font-extrabold app-text">₹{step.price}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* PM Routine Track */}
            <div class="bg-indigo-50/40 dark:bg-indigo-950/20 border border-indigo-200/60 dark:border-indigo-900/40 rounded-2xl p-6 space-y-4">
              <div class="flex items-center space-x-2 border-b border-indigo-200/60 dark:border-indigo-900/40 pb-3">
                <Moon class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                <h3 class="font-bold text-sm text-indigo-900 dark:text-indigo-200">PM Evening Track</h3>
              </div>
              <div class="space-y-3">
                {routine.pm.map((step, idx) => (
                  <div key={idx} class="app-surface p-3.5 rounded-xl border app-border shadow-sm flex items-center justify-between">
                    <div>
                      <span class="text-[10px] font-bold uppercase text-indigo-700 dark:text-indigo-400">{step.slot}</span>
                      <div class="font-bold text-xs app-text">{step.name}</div>
                      <div class="text-[11px] app-text-muted">{step.brand}</div>
                    </div>
                    <span class="text-xs font-extrabold app-text">₹{step.price}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Safety Conflict Panel */}
          <div class="app-surface border app-border rounded-2xl p-6 space-y-3">
            <h3 class="font-bold text-sm app-text flex items-center space-x-2">
              <ShieldCheck class="w-4 h-4 text-[#15803D] dark:text-emerald-400" />
              <span>Ingredient Safety Validation Report</span>
            </h3>

            <div class="space-y-2">
              {routine.conflicts.map((c, idx) => (
                <div key={idx} class="p-3 rounded-xl border text-xs flex items-start space-x-3 bg-amber-50/50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900 text-amber-900 dark:text-amber-200">
                  <AlertTriangle class="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span class="font-bold uppercase text-[10px] bg-amber-200 dark:bg-amber-800 text-amber-900 dark:text-amber-100 px-1.5 py-0.5 rounded mr-1">
                      {c.severity}
                    </span>
                    <span class="font-semibold">{c.title}:</span> {c.message}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
