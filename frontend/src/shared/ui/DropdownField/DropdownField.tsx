import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useId, useRef, useState } from 'react';

import Arrow from '@/shared/assets/icons/down-arrow.svg?react';
import clsx from 'clsx';
import s from './DropdownField.module.scss';

export type DropdownOption = {
  label: string;
  value: string;
};

type DropdownFieldProps = {
  label?: string;
  options: DropdownOption[];
  placeholder: string;
  className?: string;
  iconVariant?: 'plus' | 'chevron';
  value?: string;
  onChange?: (value: string) => void;
};

export function DropdownField({
  className,
  iconVariant = 'plus',
  label,
  onChange,
  options,
  placeholder,
  value,
}: DropdownFieldProps) {
  const [isOpen, setIsOpen] = useState(false);
  const fieldRef = useRef<HTMLDivElement>(null);
  const listId = useId();
  const selectedOption = options.find((option) => option.value === value);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handlePointerDown = (event: PointerEvent) => {
      if (!fieldRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('pointerdown', handlePointerDown);

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
    };
  }, [isOpen]);

  const handleSelect = (nextValue: string) => {
    onChange?.(nextValue);
    setIsOpen(false);
  };

  return (
    <div className={clsx(s.field, className)} ref={fieldRef}>
      {label ? <span className={s.label}>{label}</span> : null}

      <button
        className={clsx(
          s.trigger,
          iconVariant === 'chevron' && s.triggerChevron,
          isOpen && s.triggerOpen,
        )}
        type="button"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={listId}
        onClick={() => setIsOpen((current) => !current)}
      >
        <span>{selectedOption?.label ?? placeholder}</span>
        <span className={s.icon} aria-hidden="true">
          <Arrow />
        </span>
      </button>

      <AnimatePresence initial={false}>
        {isOpen ? (
          <motion.div
            className={s.menu}
            id={listId}
            role="listbox"
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
          >
            {options.map((option) => (
              <button
                className={clsx(
                  s.option,
                  option.value === value && s.optionActive,
                )}
                key={option.value}
                type="button"
                role="option"
                aria-selected={option.value === value}
                onClick={() => handleSelect(option.value)}
              >
                {option.label}
              </button>
            ))}
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
