import { Music2 } from 'lucide-react';

/**
 * Skeleton loader for grids of cards. Renders `count` placeholder tiles with
 * a subtle pulse animation. Honors prefers-reduced-motion.
 */
export function SkeletonGrid({ count = 8 }) {
  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5 gap-5"
      role="status"
      aria-label="Cargando resultados"
    >
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="glass-panel rounded-2xl p-4 space-y-3 animate-pulse motion-reduce:animate-none"
        >
          <div className="aspect-square w-full rounded-xl bg-slate-800/80 flex items-center justify-center">
            <Music2 className="w-10 h-10 text-slate-700" aria-hidden="true" />
          </div>
          <div className="h-3 w-3/4 rounded bg-slate-800/80" />
          <div className="h-2 w-1/2 rounded bg-slate-800/60" />
          <div className="h-8 w-full rounded bg-slate-800/60" />
        </div>
      ))}
    </div>
  );
}

