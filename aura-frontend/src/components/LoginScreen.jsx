import { useState } from 'react';
import { Key, ShieldCheck, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { toast } from 'sonner';

export function LoginScreen({ onAuthenticated }) {
  const [token, setToken] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token.trim()) return;
    setIsSubmitting(true);
    setError('');
    try {
      await api.login(token.trim());
      toast.success('Autenticado');
      onAuthenticated();
    } catch {
      setError('Token inválido. Inténtalo de nuevo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center p-6 selection:bg-indigo-500 selection:text-white">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8 space-y-3">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-slate-900/80 border border-indigo-500/30 p-2 items-center justify-center shadow-lg shadow-indigo-500/20">
            <img src="/aura-logo.png" alt="Aura Logo" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-indigo-300">
            Aura <span className="text-indigo-400">Music</span>
          </h1>
          <p className="text-xs text-slate-400 font-medium">Audiophile & Lossless Downloader</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="glass-panel rounded-2xl p-6 border border-slate-800/80 space-y-5"
          aria-labelledby="login-title"
        >
          <div className="flex items-center gap-2 text-slate-300">
            <ShieldCheck className="w-5 h-5 text-indigo-400" aria-hidden="true" />
            <h2 id="login-title" className="font-bold text-base">Acceso seguro</h2>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Este servicio requiere un token de acceso. Se guarda cifrado en tu navegador y nunca se envía a terceros.
          </p>

          <div className="space-y-2">
            <label htmlFor="auth-token" className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
              <Key className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
              Token de acceso
            </label>
            <input
              id="auth-token"
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Pega tu token aquí..."
              autoComplete="off"
              autoFocus
              className="w-full glass-input rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
            {error && (
              <p className="text-[11px] text-rose-400 font-semibold" role="alert">{error}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !token.trim()}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Verificando...
              </>
            ) : (
              'Entrar'
            )}
          </button>
        </form>

        <p className="text-center text-[11px] text-slate-500 mt-6">
          Si no tienes un token, contacta al administrador del servidor.
        </p>
      </div>
    </div>
  );
}

