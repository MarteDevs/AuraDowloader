import React from 'react';
import { Sparkles, Music, ShieldCheck } from 'lucide-react';

export function QualityBadge({ badge, engine, hasFlac }) {
  if (badge?.includes('FLAC') || hasFlac) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 shadow-sm">
        <Sparkles className="w-3 h-3 text-amber-400" />
        FLAC Lossless
      </span>
    );
  }

  if (badge?.includes('320k') || engine === 'youtube') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
        <ShieldCheck className="w-3 h-3 text-indigo-400" />
        HQ 320kbps
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
      <Music className="w-3 h-3 text-slate-400" />
      Standard
    </span>
  );
}
