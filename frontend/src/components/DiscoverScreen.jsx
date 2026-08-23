import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Filter, Loader2 } from 'lucide-react';
import ProductCard from './ProductCard';

const PLACEHOLDERS = [
  "gentle cleanser for sensitive skin under ₹800",
  "vitamin C serum that won't pill under sunscreen",
  "fragrance-free moisturizer for oily acne-prone skin",
  "hydrating hyaluronic acid serum for dry winter skin"
];

export default function DiscoverScreen() {
  const [query, setQuery] = useState('');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState([]);
  const [searchMeta, setSearchMeta] = useState(null);

  const [filters, setFilters] = useState({
    skin_types: [],
    concerns: [],
    pregnancy_safe: false,
    fragrance_free: false
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % PLACEHOLDERS.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  const abortRef = React.useRef(null);

  const handleSearch = async (e, customFilters = filters) => {
    if (e) e.preventDefault();

    if (abortRef.current) {
      abortRef.current.abort();
    }
    const controller = new AbortController();
    abortRef.current = controller;

    const searchQuery = query.trim() || PLACEHOLDERS[placeholderIndex];
    setLoading(true);

    try {
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          query: searchQuery,
          top_k: 6,
          skin_types: customFilters.skin_types,
          concerns: customFilters.concerns,
          pregnancy_safe: customFilters.pregnancy_safe,
          fragrance_free: customFilters.fragrance_free
        })
      });

      const data = await response.json();
      setProducts(data.recommendations || []);
      setSearchMeta({
        latency_ms: data.latency_ms,
        count: (data.recommendations || []).length
      });
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error("Search failed:", err);
      }
    } finally {
      if (abortRef.current === controller) {
        setLoading(false);
      }
    }
  };

  const toggleFilter = (type, val) => {
    setFilters((prev) => {
      const updated = { ...prev };
      if (type === 'skin_type') {
        updated.skin_types = prev.skin_types.includes(val)
          ? prev.skin_types.filter((s) => s !== val)
          : [...prev.skin_types, val];
      } else if (type === 'concern') {
        updated.concerns = prev.concerns.includes(val)
          ? prev.concerns.filter((c) => c !== val)
          : [...prev.concerns, val];
      } else if (type === 'pregnancy') {
        updated.pregnancy_safe = !prev.pregnancy_safe;
      } else if (type === 'fragrance') {
        updated.fragrance_free = !prev.fragrance_free;
      }
      handleSearch(null, updated);
      return updated;
    });
  };

  useEffect(() => {
    handleSearch();
  }, []);

  return (
    <div class="space-y-8">
      {/* Search Header Hero */}
      <div class="text-center max-w-2xl mx-auto space-y-4 pt-4">
        <h1 class="text-3xl sm:text-4xl font-extrabold app-text tracking-tight">
          Find Your Perfect Skincare Match
        </h1>
        <p class="app-text-muted text-sm sm:text-base leading-relaxed">
          Powered by hybrid vector search and deterministic ingredient safety validation.
        </p>

        {/* Search Input Bar */}
        <form onSubmit={handleSearch} class="relative max-w-xl mx-auto mt-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`e.g. "${PLACEHOLDERS[placeholderIndex]}"`}
            class="w-full pl-5 pr-28 py-3.5 app-surface border app-border rounded-full shadow-sm text-sm app-text focus:outline-none focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/20 transition"
          />
          <button
            type="submit"
            disabled={loading}
            class="absolute right-1.5 top-1.5 bottom-1.5 px-6 bg-[var(--accent)] hover:opacity-90 text-white text-sm font-medium rounded-full transition shadow-sm flex items-center space-x-1 disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <Loader2 class="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Search class="w-3.5 h-3.5 mr-1" />
                <span>Search</span>
              </>
            )}
          </button>
        </form>

        {/* Filter Chips */}
        <div class="flex flex-wrap items-center justify-center gap-2 pt-2 text-xs">
          <span class="app-text-muted font-semibold flex items-center mr-1">
            <Filter class="w-3 h-3 mr-1" /> Quick Filters:
          </span>
          
          <button
            onClick={() => toggleFilter('skin_type', 'oily')}
            class={`pill-chip cursor-pointer ${filters.skin_types.includes('oily') ? 'active' : ''}`}
          >
            Oily Skin
          </button>
          
          <button
            onClick={() => toggleFilter('skin_type', 'sensitive')}
            class={`pill-chip cursor-pointer ${filters.skin_types.includes('sensitive') ? 'active' : ''}`}
          >
            Sensitive Skin
          </button>
          
          <button
            onClick={() => toggleFilter('skin_type', 'dry')}
            class={`pill-chip cursor-pointer ${filters.skin_types.includes('dry') ? 'active' : ''}`}
          >
            Dry Skin
          </button>

          <button
            onClick={() => toggleFilter('concern', 'acne')}
            class={`pill-chip cursor-pointer ${filters.concerns.includes('acne') ? 'active' : ''}`}
          >
            Acne Concern
          </button>

          <button
            onClick={() => toggleFilter('pregnancy', 'pregnancy')}
            class={`pill-chip cursor-pointer ${filters.pregnancy_safe ? 'active' : ''}`}
          >
            Pregnancy Safe
          </button>

          <button
            onClick={() => toggleFilter('fragrance', 'fragrance')}
            class={`pill-chip cursor-pointer ${filters.fragrance_free ? 'active' : ''}`}
          >
            Fragrance Free
          </button>
        </div>
      </div>

      {/* Results Header Bar */}
      <div class="space-y-4">
        <div class="flex items-center justify-between border-b app-border pb-3">
          <h2 class="text-lg font-bold app-text flex items-center space-x-2">
            <span>Recommended Products</span>
            {searchMeta && (
              <span class="text-xs bg-[var(--accent-soft)] text-[var(--accent)] font-semibold px-2.5 py-0.5 rounded-full border border-[var(--accent)]/30">
                {searchMeta.count} items
              </span>
            )}
          </h2>

          {searchMeta && (
            <span class="text-xs app-text-muted font-mono">
              Latency: {searchMeta.latency_ms} ms
            </span>
          )}
        </div>

        {/* Results Grid */}
        {loading ? (
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div key={n} class="app-surface border app-border rounded-2xl p-6 h-64 animate-pulse space-y-4">
                <div class="h-4 app-surface-alt rounded w-1/3"></div>
                <div class="h-6 app-surface-alt rounded w-3/4"></div>
                <div class="h-4 app-surface-alt rounded w-1/4"></div>
                <div class="h-16 app-surface-alt rounded"></div>
              </div>
            ))}
          </div>
        ) : products.length > 0 ? (
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        ) : (
          <div class="col-span-full py-16 text-center space-y-3 app-surface rounded-2xl border app-border p-8 shadow-sm">
            <div class="w-12 h-12 bg-[var(--accent-soft)] text-[var(--accent)] rounded-full flex items-center justify-center mx-auto text-xl font-bold">
              <Sparkles class="w-6 h-6" />
            </div>
            <h3 class="text-base font-semibold app-text">No products matched your exact filter combination</h3>
            <p class="text-xs app-text-muted max-w-md mx-auto">
              Try clearing some active filters or modifying your search terms to browse over 8,000 Sephora catalog items.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
