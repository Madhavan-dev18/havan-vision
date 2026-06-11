import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../api';
import Sidebar from '../components/Sidebar';
import MessageBubble from '../components/MessageBubble';
import TypingIndicator from '../components/TypingIndicator';
import ChatInput from '../components/ChatInput';
import EmotionBadge from '../components/EmotionBadge';
import WebcamScanner from '../components/WebcamScanner';
import { Brain, Sparkles } from 'lucide-react';
import { emotionColor } from '../utils/emotions';

export default function Chat() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  
  const [latestEmotion, setLatestEmotion] = useState(null);
  const [visualEmotion, setVisualEmotion] = useState("neutral");

  const scrollRef = useRef(null);

  const loadSessions = useCallback(async () => {
    try {
      const res = await api.get('/chat/sessions');
      setSessions(res.data.sessions);
      return res.data.sessions;
    } catch (err) {
      setError('Could not load conversations.');
      return [];
    } finally {
      setLoadingSessions(false);
    }
  }, []);

  const loadSession = useCallback(async (sessionId) => {
    setLoadingMessages(true);
    setError('');
    try {
      const res = await api.get(`/chat/sessions/${sessionId}`);
      setMessages(res.data.messages);
      const lastUserMsg = [...res.data.messages].reverse().find((m) => m.role === 'user' && m.emotion);
      setLatestEmotion(lastUserMsg?.emotion || null);
    } catch (err) {
      setError('Could not load this conversation.');
    } finally {
      setLoadingMessages(false);
    }
  }, []);

  useEffect(() => {
    (async () => {
      const list = await loadSessions();
      if (list.length > 0) {
        setActiveSessionId(list[0].id);
      }
    })();
  }, [loadSessions]);

  useEffect(() => {
    if (activeSessionId) {
      loadSession(activeSessionId);
    } else {
      setMessages([]);
      setLatestEmotion(null);
    }
  }, [activeSessionId, loadSession]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, sending]);

  const handleNewSession = async () => {
    try {
      const res = await api.post('/chat/sessions', { title: 'New conversation' });
      setSessions((prev) => [res.data.session, ...prev]);
      setActiveSessionId(res.data.session.id);
      setMessages([]);
      setLatestEmotion(null);
    } catch (err) {
      setError('Could not start a new conversation.');
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await api.delete(`/chat/sessions/${sessionId}`);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        const remaining = sessions.filter((s) => s.id !== sessionId);
        setActiveSessionId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch (err) {
      setError('Could not delete this conversation.');
    }
  };

  const handleSend = async (content) => {
    let sessionId = activeSessionId;

    if (!sessionId) {
      try {
        const res = await api.post('/chat/sessions', { title: 'New conversation' });
        sessionId = res.data.session.id;
        setSessions((prev) => [res.data.session, ...prev]);
        setActiveSessionId(sessionId);
      } catch (err) {
        setError('Could not start a new conversation.');
        return;
      }
    }

    const optimisticUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content, // Keep the UI clean, don't show brackets to the user instantly
      created_at: new Date().toISOString(),
      emotion: null,
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);
    setSending(true);
    setError('');

    // The dirty hack: appending visual context directly to the text payload
    const finalContent = visualEmotion !== "neutral" 
      ? `${content} [My current facial expression is: ${visualEmotion}]` 
      : content;

    try {
      // Send content AND visualEmotion as separate, clean JSON variables
      const res = await api.post(`/chat/sessions/${sessionId}/messages`, { 
        content: content,
        visual_emotion: visualEmotion 
      });
      
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== optimisticUserMsg.id),
        res.data.user_message, // No more regex cleanup needed!
        res.data.assistant_message,
      ]);
      setLatestEmotion(res.data.emotion);

      setMessages((prev) => [
        ...prev.filter((m) => m.id !== optimisticUserMsg.id),
        cleanUserMsg,
        res.data.assistant_message,
      ]);
      setLatestEmotion(res.data.emotion);

      const updated = await loadSessions();
      const stillExists = updated.find((s) => s.id === sessionId);
      if (stillExists) setActiveSessionId(sessionId);
    } catch (err) {
      setError(err.response?.data?.error || 'Message could not be sent. Please try again.');
      setMessages((prev) => prev.filter((m) => m.id !== optimisticUserMsg.id));
    } finally {
      setSending(false);
    }
  };

  const accentColor = latestEmotion?.primary ? emotionColor(latestEmotion.primary) : '#2563EB';

  return (
    <div className="h-screen flex bg-mist overflow-hidden">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
      />

      <main className="flex-1 flex flex-col h-screen min-w-0 relative">
        {/* Header */}
        <header className="border-b border-azure-100 bg-white/80 backdrop-blur-sm px-6 py-4 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3 ml-12 md:ml-0">
            <div>
              <h2 className="font-display font-semibold text-ink text-lg leading-tight truncate max-w-sm md:max-w-md">
                {sessions.find((s) => s.id === activeSessionId)?.title || 'New conversation'}
              </h2>
              <p className="text-xs text-azure-700/50">MoodLens responds with emotional context</p>
            </div>
          </div>
          {latestEmotion && <EmotionBadge emotion={latestEmotion} />}
        </header>

        <div className="flex-1 flex overflow-hidden">
          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col relative overflow-hidden">
            <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 py-6 scrollbar-thin">
              <div className="max-w-3xl mx-auto space-y-5">
                {loadingMessages ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="w-6 h-6 border-2 border-azure-200 border-t-azure-600 rounded-full animate-spin" />
                  </div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center text-center py-20 animate-fade-in">
                    <div
                      className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 shadow-soft"
                      style={{ backgroundColor: `${accentColor}15` }}
                    >
                      <Sparkles className="w-7 h-7" style={{ color: accentColor }} />
                    </div>
                    <h3 className="font-display text-xl font-semibold text-ink mb-2">
                      How are you feeling today?
                    </h3>
                    <p className="text-sm text-azure-700/60 max-w-sm">
                      MoodLens listens, detects the emotion behind your words, and responds with
                      genuine empathy and context.
                    </p>
                  </div>
                ) : (
                  messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
                )}

                {sending && <TypingIndicator />}
              </div>
            </div>

            {/* Error banner */}
            {error && (
              <div className="px-4 md:px-8 shrink-0">
                <div className="max-w-3xl mx-auto mb-2 text-sm text-rose-600 bg-rose-50 border border-rose-100 rounded-xl px-4 py-2.5 animate-fade-in">
                  {error}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="border-t border-azure-100 bg-white/80 backdrop-blur-sm px-4 md:px-8 py-4 shrink-0">
              <div className="max-w-3xl mx-auto">
                <ChatInput onSend={handleSend} disabled={sending} />
                <p className="text-xs text-azure-700/40 text-center mt-2 flex items-center justify-center gap-1.5">
                  <Brain className="w-3 h-3" />
                  MoodLens is a supportive companion, not a substitute for professional care.
                </p>
              </div>
            </div>
          </div>

          {/* Right Panel: Visual Cortex Omni-Sensor (Desktop Only) */}
          <div className="w-80 border-l border-azure-100 bg-white/50 p-6 hidden xl:block overflow-y-auto shrink-0">
            <WebcamScanner onEmotionDetected={setVisualEmotion} />
            <div className="mt-6 text-xs text-azure-700/70 leading-relaxed bg-azure-50 p-4 rounded-xl border border-azure-100">
              <p className="font-semibold text-ink mb-2 flex items-center gap-2">
                <Brain className="w-4 h-4 text-azure-600" />
                Omni-Sensor Active
              </p>
              J.A.R.V.I.S. is monitoring your facial micro-expressions in real-time. This visual telemetry is fused with your text input to generate a highly accurate, composite emotional profile.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}