type LocalizedEntity = Record<string, unknown>;

function getLanguageSuffix(language: string) {
  const normalizedLanguage = language.toLowerCase();

  if (normalizedLanguage.startsWith('ru')) {
    return 'ru';
  }

  if (normalizedLanguage.startsWith('en')) {
    return 'en';
  }

  if (normalizedLanguage.startsWith('uz')) {
    return 'uz';
  }

  return null;
}

export function getLocalizedField<T extends LocalizedEntity>(
  entity: T,
  field: string,
  language: string,
) {
  const languageSuffix = getLanguageSuffix(language);
  const localizedValue =
    languageSuffix && entity[`${field}_${languageSuffix}`];
  const fallbackValue = entity[field];

  if (typeof localizedValue === 'string' && localizedValue.length > 0) {
    return localizedValue;
  }

  if (typeof fallbackValue === 'string') {
    return fallbackValue;
  }

  return '';
}
