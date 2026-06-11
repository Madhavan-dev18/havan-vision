import { emotionColor, emotionEmoji, emotionLabel } from '../utils/emotions';

export default function EmotionBadge({ emotion, compact = false }) {
  if (!emotion || !emotion.primary) return null;

  const { primary, sentiment, intensity } = emotion;
  const color = emotionColor(primary);

  if (compact) {
    return (
      <span
        className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full"
        style={{ backgroundColor: `${color}18`, color }}
      >
        <span>{emotionEmoji(primary)}</span>
        {emotionLabel(primary)}
      </span>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 text-xs px-2.5 py-1 rounded-lg bg-white/70 border border-azure-100">
      <span className="text-base leading-none">{emotionEmoji(primary)}</span>
      <span className="font-semibold" style={{ color }}>{emotionLabel(primary)}</span>
      {sentiment && (
        <span className="text-azure-700/40">
          · {sentiment}
        </span>
      )}
      {typeof intensity === 'number' && (
        <span className="flex items-center gap-1">
          <span className="w-12 h-1.5 rounded-full bg-azure-100 overflow-hidden">
            <span
              className="block h-full rounded-full"
              style={{ width: `${Math.round(intensity * 100)}%`, backgroundColor: color }}
            />
          </span>
        </span>
      )}
    </div>
  );
}
