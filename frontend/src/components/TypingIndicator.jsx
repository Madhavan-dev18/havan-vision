import { Brain } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 bg-white border border-azure-100">
        <Brain className="w-4 h-4 text-azure-600" />
      </div>
      <div className="px-4 py-3.5 rounded-2xl rounded-tl-md bg-white border border-azure-100 shadow-soft flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-azure-300 animate-pulse-soft" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 rounded-full bg-azure-300 animate-pulse-soft" style={{ animationDelay: '200ms' }} />
        <span className="w-2 h-2 rounded-full bg-azure-300 animate-pulse-soft" style={{ animationDelay: '400ms' }} />
      </div>
    </div>
  );
}
