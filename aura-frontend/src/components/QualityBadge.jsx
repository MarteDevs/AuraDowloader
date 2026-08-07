import { Sparkles, Music, ShieldCheck } from 'lucide-react';

export function QualityBadge({ badge, engine, hasFlac }) {
  if (badge?.includes('FLAC') || hasFlac) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-950/85 backdrop-blur-md text-amber-400 border border-amber-500/30 shadow-md">
        <Sparkles className="w-3 h-3 text-amber-400" />
        FLAC Lossless
      </span>
    );
  }

  if (badge?.includes('320k') || engine === 'youtube') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-950/85 backdrop-blur-md text-indigo-300 border border-indigo-500/30 shadow-md">
        <ShieldCheck className="w-3 h-3 text-indigo-400" />
        HQ 320kbps
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-950/85 backdrop-blur-md text-slate-300 border border-slate-700/60 shadow-md">
      <Music className="w-3 h-3 text-slate-400" />
      Standard
    </span>
  );
}

