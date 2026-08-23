import React from 'react';

export default function Footer() {
  return (
    <footer class="border-t app-border app-surface py-6 mt-12 text-center text-xs app-text-muted px-6 transition-colors duration-250">
      <div class="max-w-[1180px] mx-auto space-y-2">
        <p class="leading-relaxed">
          GlowMatch provides cosmetic product matching based on automated analysis. It is not dermatological or medical advice. Visual tone estimation depends on lighting and image quality. Consult a qualified professional for skin health concerns.
        </p>
        <p class="text-[10px] app-text-muted/70 font-mono">
          GlowMatch AI — FastAPI + React + Qdrant + BAAI Hybrid Retrieval Architecture
        </p>
      </div>
    </footer>
  );
}
