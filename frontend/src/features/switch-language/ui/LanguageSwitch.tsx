import { AnimatePresence, motion } from 'framer-motion';
import { LANGUAGES, type Language } from '@/shared/i18n';

import clsx from 'clsx';
import s from './LanguageSwitch.module.scss';
import { Fragment, useState } from 'react';
import { useTranslation } from 'react-i18next';

export function LanguageSwitch() {
  const { i18n } = useTranslation();
  const language = i18n.language as Language;
  const [isOpen, setIsOpen] = useState(false);
  const changeLanguage = (nextLanguage: Language) => {
    i18n.changeLanguage(nextLanguage);
  };

  return (
    <div className={s.root}>
      <div className={s.langList} role="tablist" aria-label="Language">
        {LANGUAGES.map((lang) => {
          const isActive = lang === language;
          return (
            <Fragment key={lang}>
              <button
                className={clsx(s.langBtn, isActive && s.langBtnActive)}
                aria-current={isActive ? 'true' : undefined}
                onClick={() => changeLanguage(lang)}
              >
                {lang}
              </button>
              {lang !== LANGUAGES[LANGUAGES.length - 1] ? (
                <span className={s.langDivider} aria-hidden="true">
                  /
                </span>
              ) : null}
            </Fragment>
          );
        })}
      </div>

      <div className={s.langSelect}>
        <button
          className={s.langSelectBtn}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          onClick={() => setIsOpen((v) => !v)}
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.span
              key={language}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 4 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
            >
              {language}
            </motion.span>
          </AnimatePresence>
        </button>
        <AnimatePresence>
          {isOpen ? (
            <motion.div
              className={s.langSelectList}
              role="listbox"
              aria-label="Language"
              initial={{ opacity: 0, y: -6, x: '-50%' }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
            >
              {LANGUAGES.map((lang) => {
                const isActive = lang === language;
                return (
                  <button
                    key={lang}
                    className={clsx(
                      s.langSelectItem,
                      isActive && s.langSelectItemActive,
                    )}
                    role="option"
                    aria-selected={isActive}
                    onClick={() => {
                      changeLanguage(lang);
                      setIsOpen(false);
                    }}
                  >
                    {lang}
                  </button>
                );
              })}
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
}
