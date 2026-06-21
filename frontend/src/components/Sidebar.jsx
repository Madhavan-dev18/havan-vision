import { useState } from 'react';
import { Plus, MessageSquare, Trash2, LogOut, Brain, Menu, X } from 'lucide-react';
import { emotionColor, emotionEmoji } from '../utils/emotions';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ sessions, activeSessionId, onSelectSession, onNewSession, onDeleteSession }) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);

  const formatDate = (iso) => {
    const date = new Date(iso);
    const today = new Date();
    if (date.toDateString() === today.toDateString()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  const SidebarContent = (
    <div className="flex flex-col h-full">
      <div className="p-5 border-b border-azure-100">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-azure-600 flex items-center justify-center shrink-0">
            <Brain className="w-5 h-5 text-white" strokeWidth={2} />
          </div>
          <div>
            <h1 className="font-display font-semibold text-ink leading-tight">Havan Vision</h1>
            <p className="text-xs text-azure-700/60">Emotion-aware AI</p>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="ml-auto md:hidden p-1.5 rounded-lg hover:bg-azure-50 text-azure-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="p-3">
        <button
          onClick={() => { onNewSession(); setOpen(false); }}
          className="w-full flex items-center justify-center gap-2 bg-azure-600 hover:bg-azure-700 text-white font-semibold py-2.5 rounded-xl transition-colors shadow-soft text-sm"
        >
          <Plus className="w-4 h-4" />
          New conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1 scrollbar-thin">
        {sessions.length === 0 && (
          <p className="text-xs text-azure-700/50 text-center mt-8 px-4">
            No conversations yet. Start a new one to begin.
          </p>
        )}
        {sessions.map((s) => (
          <button
            key={s.id}
            onClick={() => { onSelectSession(s.id); setOpen(false); }}
            className={`w-full text-left px-3 py-2.5 rounded-xl transition-colors group flex items-start gap-2.5 ${
              activeSessionId === s.id
                ? 'bg-azure-100/70 border border-azure-200'
                : 'hover:bg-azure-50 border border-transparent'
            }`}
          >
            <div className="mt-0.5 shrink-0">
              {s.dominant_emotion ? (
                <span
                  className="w-7 h-7 rounded-lg flex items-center justify-center text-sm"
                  style={{ backgroundColor: `${emotionColor(s.dominant_emotion)}20` }}
                >
                  {emotionEmoji(s.dominant_emotion)}
                </span>
              ) : (
                <span className="w-7 h-7 rounded-lg bg-azure-50 flex items-center justify-center">
                  <MessageSquare className="w-3.5 h-3.5 text-azure-400" />
                </span>
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-ink truncate">{s.title}</p>
              <p className="text-xs text-azure-700/50">{formatDate(s.updated_at)}</p>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); onDeleteSession(s.id); }}
              className="opacity-0 group-hover:opacity-100 p-1 rounded-md hover:bg-rose-50 text-azure-300 hover:text-rose-500 transition-all shrink-0"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </button>
        ))}
      </div>

      <div className="p-3 border-t border-azure-100">
        <div className="flex items-center gap-3 px-2 py-2">
          <div className="w-9 h-9 rounded-xl bg-azure-50 border border-azure-100 flex items-center justify-center text-lg shrink-0">
            {user?.avatar_emoji || '🧠'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold text-ink truncate">{user?.display_name || user?.username}</p>
            <p className="text-xs text-azure-700/50 truncate">@{user?.username}</p>
          </div>
          <button
            onClick={logout}
            title="Sign out"
            className="p-2 rounded-lg hover:bg-rose-50 text-azure-400 hover:text-rose-500 transition-colors shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setOpen(true)}
        className="md:hidden fixed top-4 left-4 z-30 p-2.5 bg-white rounded-xl shadow-card border border-azure-100"
      >
        <Menu className="w-5 h-5 text-azure-700" />
      </button>

      {/* Mobile drawer */}
      {open && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="absolute inset-0 bg-ink/30 backdrop-blur-sm" onClick={() => setOpen(false)} />
          <div className="relative w-72 bg-white shadow-2xl animate-slide-up">{SidebarContent}</div>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-72 shrink-0 bg-white border-r border-azure-100 flex-col h-screen">
        {SidebarContent}
      </aside>
    </>
  );
}
