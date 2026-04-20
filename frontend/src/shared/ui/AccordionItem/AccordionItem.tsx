import { AnimatePresence, motion } from 'framer-motion';
import type { ReactNode } from 'react';

import clsx from 'clsx';
import s from './AccordionItem.module.scss';

type AccordionItemProps = {
  children: ReactNode;
  isOpen: boolean;
  title: ReactNode;
  bodyClassName?: string;
  buttonClassName?: string;
  className?: string;
  contentClassName?: string;
  iconClassName?: string;
  iconOpenClassName?: string;
  onToggle: () => void;
};

export function AccordionItem({
  bodyClassName,
  buttonClassName,
  children,
  className,
  contentClassName,
  iconClassName,
  iconOpenClassName,
  isOpen,
  onToggle,
  title,
}: AccordionItemProps) {
  return (
    <section className={clsx(s.accordionItem, className)}>
      <button
        className={clsx(s.trigger, buttonClassName)}
        type="button"
        aria-expanded={isOpen}
        onClick={onToggle}
      >
        <span>{title}</span>
        <span
          className={clsx(
            s.icon,
            iconClassName,
            isOpen && s.iconOpen,
            isOpen && iconOpenClassName,
          )}
          aria-hidden="true"
        />
      </button>

      <AnimatePresence initial={false}>
        {isOpen ? (
          <motion.div
            className={clsx(s.body, bodyClassName)}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
          >
            <div className={clsx(s.content, contentClassName)}>{children}</div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </section>
  );
}
