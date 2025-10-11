import { createI18n, type useI18n } from 'vue-i18n';
import de from './de.json';
import en from './en.json';
const supportedLocales = ['en', 'de'];
const defaultLocale = 'de';

export type T = ReturnType<typeof useI18n>['t'];

const getUserPreferredLocale = () => {
  const browserLocale = navigator.language;
  return supportedLocales.includes(browserLocale) ? browserLocale : defaultLocale;
}

export const i18n = createI18n({
  // Force German UI by default
  locale: 'de',
  messages: { 'de': de, 'en': en },
  fallbackLocale: defaultLocale
});
