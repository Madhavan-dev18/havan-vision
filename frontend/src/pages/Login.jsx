import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Brain, ArrowRight, Loader2 } from 'lucide-react';

export default function Login() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(identifier, password);
      navigate('/chat');
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-aurora bg-grid flex items-center justify-center px-4">
      <div className="w-full max-w-md animate-slide-up">
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-azure-600 flex items-center justify-center shadow-soft mb-4">
            <Brain className="w-7 h-7 text-white" strokeWidth={2} />
          </div>
          <h1 className="font-display text-3xl font-semibold text-ink tracking-tight">Havan Vision</h1>
          <p className="text-azure-700/70 text-sm mt-1">Welcome back. Let's pick up where you left off.</p>
        </div>

        <div className="bg-white/80 backdrop-blur-sm border border-azure-100 rounded-3xl shadow-card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-ink mb-1.5">Username or email</label>
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl border border-azure-100 bg-mist focus:bg-white focus:border-azure-400 focus:ring-4 focus:ring-azure-100 outline-none transition-all text-ink placeholder:text-azure-300"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-ink mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl border border-azure-100 bg-mist focus:bg-white focus:border-azure-400 focus:ring-4 focus:ring-azure-100 outline-none transition-all text-ink placeholder:text-azure-300"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="text-sm text-rose-600 bg-rose-50 border border-rose-100 rounded-xl px-4 py-2.5 animate-fade-in">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-azure-600 hover:bg-azure-700 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-all shadow-soft flex items-center justify-center gap-2 group"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Sign in
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
                </>
              )}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-azure-700/70 mt-6">
          New to Havan Vision?{' '}
          <Link to="/register" className="text-azure-600 font-semibold hover:text-azure-800 transition-colors">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
