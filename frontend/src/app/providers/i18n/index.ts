import en from '@/shared/i18n/en.json';
import i18n from 'i18next';
import ru from '@/shared/i18n/ru.json';
import { initReactI18next } from 'react-i18next';
import uz from '@/shared/i18n/uz.json';

export const LANGUAGES = ['RU', 'UZ', 'EN'] as const;

export type Language = (typeof LANGUAGES)[number];

export const DEFAULT_LANGUAGE: Language = 'RU';

const resources = {
  RU: {
    translation: ru,
  },
  UZ: {
    translation: uz,
  },
  EN: {
    translation: en,
  },
} as const;

i18n.use(initReactI18next).init({
  resources,
  lng: DEFAULT_LANGUAGE,
  fallbackLng: DEFAULT_LANGUAGE,
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
