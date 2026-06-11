import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 160) + 'px';
    }
  }, [value]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2.5">
      <div className="flex-1 bg-white border border-azure-100 rounded-2xl shadow-soft focus-within:border-azure-300 focus-within:ring-4 focus-within:ring-azure-100 transition-all">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          maxLength={4000}
          placeholder="Share what's on your mind..."
          className="w-full px-4 py-3 bg-transparent outline-none resize-none text-sm text-ink placeholder:text-azure-300 max-h-40"
        />
      </div>
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="w-11 h-11 rounded-2xl bg-azure-600 hover:bg-azure-700 disabled:opacity-40 disabled:cursor-not-allowed text-white flex items-center justify-center shrink-0 transition-all shadow-soft"
      >
        <Send className="w-4.5 h-4.5" />
      </button>
    </form>
  );
}
