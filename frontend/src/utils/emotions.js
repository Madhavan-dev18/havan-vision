export const EMOTION_COLORS = {
  joy: '#F5A524',
  sadness: '#3B82F6',
  anger: '#E11D48',
  fear: '#7C3AED',
  surprise: '#0EA5E9',
  disgust: '#64748B',
  neutral: '#94A3B8',
};

export const EMOTION_EMOJI = {
  joy: '😄',
  sadness: '😢',
  anger: '😠',
  fear: '😰',
  surprise: '😲',
  disgust: '🤢',
  neutral: '😐',
};

export const EMOTION_LABELS = {
  joy: 'Joy',
  sadness: 'Sadness',
  anger: 'Anger',
  fear: 'Fear',
  surprise: 'Surprise',
  disgust: 'Disgust',
  neutral: 'Neutral',
};

export function emotionColor(name) {
  return EMOTION_COLORS[name] || EMOTION_COLORS.neutral;
}

export function emotionEmoji(name) {
  return EMOTION_EMOJI[name] || EMOTION_EMOJI.neutral;
}

export function emotionLabel(name) {
  return EMOTION_LABELS[name] || 'Neutral';
}
