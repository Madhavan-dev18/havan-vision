import { Brain, User } from 'lucide-react';
import EmotionBadge from './EmotionBadge';
import { emotionColor } from '../utils/emotions';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const emotion = message.emotion;
  const accent = emotion?.primary ? emotionColor(emotion.primary) : null;

  return (
    <div className={`flex gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div
        className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
          isUser ? 'bg-azure-600' : 'bg-white border border-azure-100'
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Brain className="w-4 h-4 text-azure-600" />
        )}
      </div>

      <div className={`flex flex-col gap-1.5 max-w-[78%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-soft ${
            isUser
              ? 'bg-azure-600 text-white rounded-tr-md'
              : 'bg-white text-ink border border-azure-100 rounded-tl-md'
          }`}
          style={isUser && accent ? { boxShadow: `0 4px 16px -6px ${accent}55` } : undefined}
        >
          {message.content}
        </div>
        {isUser && emotion && <EmotionBadge emotion={emotion} compact />}
      </div>
    </div>
  );
}
