import React, { useState } from 'react';
import { Camera, Upload, Sparkles, CheckCircle2, ShieldAlert } from 'lucide-react';
import ItaGauge from './ItaGauge';

export default function AnalyzeScreen() {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleSampleClick = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setResult({
        ita: 34.2,
        ita_band: "intermediate",
        lab: [62.1, 12.4, 18.9],
        concerns: ["acne", "uneven_tone"],
        concern_confidence: { acne: 0.72, uneven_tone: 0.61 },
        face_detected: true,
        white_balance_applied: true
      });
      setAnalyzing(false);
    }, 1200);
  };

  return (
    <div class="space-y-8">
      <div class="text-center max-w-xl mx-auto space-y-2">
        <h2 class="text-2xl font-bold app-text">Selfie Skin Tone & Shade Matcher</h2>
        <p class="text-xs app-text-muted leading-relaxed">
          Determines Individual Typology Angle (ITA°) skin tone using white-balanced color science (CIE LAB) without relying on LLM tone guesswork.
        </p>
      </div>

      {!result ? (
        <div
          onClick={handleSampleClick}
          class="max-w-xl mx-auto app-surface border-2 border-dashed app-border hover:border-[var(--accent)] rounded-2xl p-10 text-center space-y-4 transition cursor-pointer shadow-sm group"
        >
          <div class="w-14 h-14 app-surface-alt group-hover:bg-[var(--accent-soft)] app-text-muted group-hover:text-[var(--accent)] rounded-full flex items-center justify-center mx-auto transition">
            <Camera class="w-7 h-7" />
          </div>

          <div>
            <p class="text-sm font-bold app-text">Upload selfie photo, or click to run sample</p>
            <p class="text-xs app-text-muted mt-1">
              Supports JPG, PNG up to 8MB. Photo is processed strictly in memory and never stored.
            </p>
          </div>

          <button
            disabled={analyzing}
            class="px-6 py-2.5 bg-[var(--accent)] hover:opacity-90 text-white text-xs font-semibold rounded-full transition shadow-sm cursor-pointer"
          >
            {analyzing ? "Analyzing Skin Regions..." : "Try Sample Analysis"}
          </button>
        </div>
      ) : (
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
          {/* Left: ITA Gauge & Color Swatch */}
          <div class="space-y-4">
            <h3 class="text-sm font-bold app-text border-b app-border pb-2">
              Color Typology Results
            </h3>
            <ItaGauge ita={result.ita} band={result.ita_band} />

            <div class="app-surface border app-border rounded-2xl p-4 flex items-center justify-between text-xs">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg border app-border shadow-inner bg-[#DCA78E]" />
                <div>
                  <div class="font-bold app-text">CIE LAB Triplet</div>
                  <div class="text-[11px] app-text-muted tabular-nums">
                    L*: {result.lab[0]}, a*: {result.lab[1]}, b*: {result.lab[2]}
                  </div>
                </div>
              </div>
              <span class="text-[10px] bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300 font-semibold px-2 py-0.5 rounded-full border border-green-200 dark:border-green-900">
                White-Balanced
              </span>
            </div>
          </div>

          {/* Right: Detected Attributes & Concerns */}
          <div class="space-y-4">
            <h3 class="text-sm font-bold app-text border-b app-border pb-2">
              Detected Skin Attributes
            </h3>

            <div class="app-surface border app-border rounded-2xl p-6 space-y-4">
              <div class="space-y-2">
                <span class="text-xs font-semibold app-text-muted">Detected Concerns</span>
                <div class="flex flex-wrap gap-2">
                  {result.concerns.map((c) => (
                    <span
                      key={c}
                      class="px-3 py-1 bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/30 rounded-full text-xs font-semibold capitalize"
                    >
                      {c.replace('_', ' ')} (72%)
                    </span>
                  ))}
                </div>
              </div>

              <div class="pt-4 border-t app-border flex items-center justify-between text-xs">
                <button
                  onClick={() => setResult(null)}
                  class="text-xs text-[var(--accent)] font-semibold hover:underline cursor-pointer"
                >
                  ← Test Another Photo
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
