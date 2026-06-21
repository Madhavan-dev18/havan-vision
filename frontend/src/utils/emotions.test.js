import { describe, it, expect } from 'vitest';
import { emotionColor, emotionEmoji, emotionLabel, EMOTION_COLORS, EMOTION_EMOJI, EMOTION_LABELS } from './emotions';

describe('emotionColor', () => {
  it('returns the correct color for known emotions', () => {
    expect(emotionColor('joy')).toBe(EMOTION_COLORS.joy);
    expect(emotionColor('sadness')).toBe(EMOTION_COLORS.sadness);
    expect(emotionColor('anger')).toBe(EMOTION_COLORS.anger);
    expect(emotionColor('fear')).toBe(EMOTION_COLORS.fear);
    expect(emotionColor('surprise')).toBe(EMOTION_COLORS.surprise);
    expect(emotionColor('disgust')).toBe(EMOTION_COLORS.disgust);
    expect(emotionColor('neutral')).toBe(EMOTION_COLORS.neutral);
  });

  it('returns neutral color for unknown emotions', () => {
    expect(emotionColor('unknown')).toBe(EMOTION_COLORS.neutral);
    expect(emotionColor('')).toBe(EMOTION_COLORS.neutral);
    expect(emotionColor(undefined)).toBe(EMOTION_COLORS.neutral);
  });
});

describe('emotionEmoji', () => {
  it('returns the correct emoji for known emotions', () => {
    expect(emotionEmoji('joy')).toBe('😄');
    expect(emotionEmoji('sadness')).toBe('😢');
    expect(emotionEmoji('anger')).toBe('😠');
    expect(emotionEmoji('fear')).toBe('😰');
    expect(emotionEmoji('surprise')).toBe('😲');
    expect(emotionEmoji('disgust')).toBe('🤢');
    expect(emotionEmoji('neutral')).toBe('😐');
  });

  it('returns neutral emoji for unknown emotions', () => {
    expect(emotionEmoji('unknown')).toBe('😐');
    expect(emotionEmoji(null)).toBe('😐');
  });
});

describe('emotionLabel', () => {
  it('returns the correct label for known emotions', () => {
    expect(emotionLabel('joy')).toBe('Joy');
    expect(emotionLabel('sadness')).toBe('Sadness');
    expect(emotionLabel('anger')).toBe('Anger');
    expect(emotionLabel('fear')).toBe('Fear');
    expect(emotionLabel('surprise')).toBe('Surprise');
    expect(emotionLabel('disgust')).toBe('Disgust');
    expect(emotionLabel('neutral')).toBe('Neutral');
  });

  it('returns "Neutral" for unknown emotions', () => {
    expect(emotionLabel('unknown')).toBe('Neutral');
    expect(emotionLabel(undefined)).toBe('Neutral');
  });
});

describe('emotion constants', () => {
  it('has consistent keys across all maps', () => {
    const colorKeys = Object.keys(EMOTION_COLORS).sort();
    const emojiKeys = Object.keys(EMOTION_EMOJI).sort();
    const labelKeys = Object.keys(EMOTION_LABELS).sort();
    expect(colorKeys).toEqual(emojiKeys);
    expect(colorKeys).toEqual(labelKeys);
  });

  it('all colors are valid hex values', () => {
    Object.values(EMOTION_COLORS).forEach((color) => {
      expect(color).toMatch(/^#[0-9A-Fa-f]{6}$/);
    });
  });
});
