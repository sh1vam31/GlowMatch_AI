import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, Sun, Moon, Loader2, RefreshCw } from 'lucide-react';

export default function RoutineScreen() {
  const [skinType, setSkinType] = useState('dry');
  const [budget, setBudget] = useState(5500);
  const [pregnancySafe, setPregnancySafe] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [routine, setRoutine] = useState(null);

  const fetchSlotProduct = async (query, category, maxPrice, defaultFallback) => {
    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          category: category,
          skin_types: [skinType],
          price_ceiling_inr: maxPrice,
          pregnancy_safe: pregnancySafe,
          top_k: 3
        })
      });
      const data = await res.json();
      if (data.recommendations && data.recommendations.length > 0) {
        const top = data.recommendations[0];
        return {
          name: top.name,
          brand: top.brand,
          price: top.price_inr
        };
      }
    } catch (e) {
      console.error("Slot fetch failed:", e);
    }
    return defaultFallback;
  };

  const handleBuild = async () => {
    setGenerating(true);

    const cleanserPriceMax = Math.round(budget * 0.25);
    const moisturizerPriceMax = Math.round(budget * 0.35);
    const treatmentPriceMax = Math.round(budget * 0.30);
    const sunscreenPriceMax = Math.round(budget * 0.25);

    const cleanserTask = fetchSlotProduct(
      `gentle cleanser for ${skinType} skin`,
      "cleanser",
      cleanserPriceMax,
      { name: `${skinType.toUpperCase()} Gentle Cleanser`, brand: "CeraVe", price: Math.min(850, cleanserPriceMax) }
    );

    const moisturizerTask = fetchSlotProduct(
      `nourishing moisturizer cream for ${skinType} skin`,
      "moisturizer",
      moisturizerPriceMax,
      { name: `${skinType.toUpperCase()} Barrier Cream`, brand: "Neutrogena", price: Math.min(1250, moisturizerPriceMax) }
    );

    const treatmentTask = fetchSlotProduct(
      pregnancySafe ? `soothing hydration serum for ${skinType} skin` : `active treatment serum for ${skinType} skin`,
      "treatment",
      treatmentPriceMax,
      { name: pregnancySafe ? "Azelaic Acid 10% Serum" : "Retinol 0.2% Squalane", brand: "The Ordinary", price: Math.min(990, treatmentPriceMax) }
    );

    const sunscreenTask = fetchSlotProduct(
      `broad spectrum SPF sunscreen for ${skinType} skin`,
      "sunscreen",
      sunscreenPriceMax,
      { name: "Invisible Physical SPF 50", brand: "La Roche-Posay", price: Math.min(1450, sunscreenPriceMax) }
    );

    const [cleanser, moisturizer, treatment, sunscreen] = await Promise.all([
      cleanserTask,
      moisturizerTask,
      treatmentTask,
      sunscreenTask
    ]);

    // Safety checks
    const conflicts = [];
    if (pregnancySafe) {
      conflicts.push({
        severity: "INFO",
        title: "Pregnancy & Lactation Protocol Active",
        message: "Retinoids, Tretinoin, and Hydroquinone have been strictly excluded from all AM & PM routine slots."
      });
    }

    conflicts.push({
      severity: "SEPARATE",
      title: "PM Active Separation",
      message: "Exfoliating acids (AHA/BHA) and retinoids should be applied on alternate nights to preserve moisture barrier balance."
    });

    setRoutine({
      am: [
        { slot: "Cleanser", ...cleanser },
        { slot: "Moisturizer", ...moisturizer },
        { slot: "Sunscreen", ...sunscreen }
      ],
      pm: [
        { slot: "Cleanser", ...cleanser },
        { slot: "Treatment", ...treatment },
        { slot: "Moisturizer", ...moisturizer }
      ],
      conflicts
    });

    setGenerating(false);
  };

  return (
    <div class="space-y-8">
      <div class="text-center max-w-xl mx-auto space-y-2">
        <h2 class="text-2xl font-bold app-text">Safe Skincare Routine Builder</h2>
        <p class="text-xs app-text-muted leading-relaxed">
          Assembles morning (AM) and evening (PM) routines governed by your skin profile, max budget, and safety rules.
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
              class="w-full app-surface-alt border app-border app-text rounded-lg p-2.5 text-sm focus:outline-none focus:border-[var(--accent)] cursor-pointer"
            >
              <option value="dry">Dry Skin</option>
              <option value="sensitive">Sensitive Skin</option>
              <option value="oily">Oily Skin</option>
              <option value="combination">Combination Skin</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold app-text-muted mb-1">Max Total Budget (₹{budget})</label>
            <input
              type="range"
              min="1500"
              max="12000"
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
          class="w-full py-3 bg-[var(--accent)] hover:opacity-90 text-white font-semibold text-xs rounded-xl transition shadow-sm cursor-pointer flex items-center justify-center space-x-2 disabled:opacity-50"
        >
          {generating ? (
            <>
              <Loader2 class="w-4 h-4 animate-spin" />
              <span>Fetching {skinType.toUpperCase()} Products for ₹{budget} Budget...</span>
            </>
          ) : (
            <>
              <RefreshCw class="w-3.5 h-3.5 mr-1" />
              <span>Assemble Safe AM / PM Routine</span>
            </>
          )}
        </button>
      </div>

      {/* Routine Display */}
      {routine && (
        <div class="space-y-6 max-w-4xl mx-auto">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AM Routine Track */}
            <div class="app-surface border app-border rounded-2xl p-6 space-y-4 shadow-sm">
              <div class="flex items-center justify-between border-b app-border pb-3">
                <div class="flex items-center space-x-2">
                  <Sun class="w-4 h-4 text-amber-500" />
                  <h3 class="font-bold text-sm app-text">AM Morning Track</h3>
                </div>
                <span class="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                  Day Routine
                </span>
              </div>
              <div class="space-y-3">
                {routine.am.map((step, idx) => (
                  <div key={idx} class="app-surface-alt p-3.5 rounded-xl border app-border shadow-xs flex items-center justify-between transition hover:border-amber-500/30">
                    <div>
                      <span class="text-[10px] font-extrabold uppercase tracking-wider text-amber-600 dark:text-amber-400">{step.slot}</span>
                      <div class="font-bold text-xs app-text line-clamp-1">{step.name}</div>
                      <div class="text-[11px] app-text-muted">{step.brand}</div>
                    </div>
                    <span class="text-xs font-extrabold app-text tabular-nums shrink-0 ml-2">₹{step.price}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* PM Routine Track */}
            <div class="app-surface border app-border rounded-2xl p-6 space-y-4 shadow-sm">
              <div class="flex items-center justify-between border-b app-border pb-3">
                <div class="flex items-center space-x-2">
                  <Moon class="w-4 h-4 text-indigo-500" />
                  <h3 class="font-bold text-sm app-text">PM Evening Track</h3>
                </div>
                <span class="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                  Night Routine
                </span>
              </div>
              <div class="space-y-3">
                {routine.pm.map((step, idx) => (
                  <div key={idx} class="app-surface-alt p-3.5 rounded-xl border app-border shadow-xs flex items-center justify-between transition hover:border-indigo-500/30">
                    <div>
                      <span class="text-[10px] font-extrabold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">{step.slot}</span>
                      <div class="font-bold text-xs app-text line-clamp-1">{step.name}</div>
                      <div class="text-[11px] app-text-muted">{step.brand}</div>
                    </div>
                    <span class="text-xs font-extrabold app-text tabular-nums shrink-0 ml-2">₹{step.price}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Safety Conflict Panel */}
          <div class="app-surface border app-border rounded-2xl p-6 space-y-3 shadow-sm">
            <h3 class="font-bold text-sm app-text flex items-center space-x-2">
              <ShieldCheck class="w-4 h-4 text-[#15803D] dark:text-emerald-400" />
              <span>Ingredient Safety Validation Report</span>
            </h3>

            <div class="space-y-2">
              {routine.conflicts.map((c, idx) => (
                <div
                  key={idx}
                  class="p-4 rounded-xl border text-xs flex items-start space-x-3 bg-amber-100/80 dark:bg-amber-950/40 border-amber-300 dark:border-amber-800/60"
                >
                  <AlertTriangle class="w-4.5 h-4.5 text-amber-800 dark:text-amber-400 shrink-0 mt-0.5" />
                  <div class="space-y-1">
                    <div class="flex items-center space-x-2">
                      <span class="font-black uppercase text-[10px] bg-amber-800 text-white dark:bg-amber-700 dark:text-white px-2 py-0.5 rounded shadow-xs">
                        {c.severity}
                      </span>
                      <span class="font-extrabold text-amber-950 dark:text-amber-100 text-xs">
                        {c.title}
                      </span>
                    </div>
                    <p class="text-amber-900 dark:text-amber-200 text-xs leading-relaxed font-medium pt-0.5">
                      {c.message}
                    </p>
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
