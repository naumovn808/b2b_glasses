export const LANGUAGES = ['RU', 'UZ', 'EN'] as const;

export type Language = (typeof LANGUAGES)[number];
