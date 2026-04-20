import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, type ReactElement, type ReactNode } from 'react';

import clsx from 'clsx';
import { createPortal } from 'react-dom';
import { useScrollLock } from 'usehooks-ts';
import s from './ModalWindowShell.module.scss';

export type ModalWindowShellPosition =
  | 'center'
  | 'top'
  | 'bottom'
  | 'left'
  | 'right'
  | 'top-left'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-right';

export type ModalWindowShellProps = {
  isOpen: boolean;
  children: ReactNode;
  className?: string;
  modalClassName?: string;
  position?: ModalWindowShellPosition;
  title?: string | ReactElement | null;
  onClose?: () => void;
};

export function ModalWindowShell({
  children,
  className,
  modalClassName,
  isOpen,
  position = 'center',
  title = null,
  onClose,
}: ModalWindowShellProps) {
  const { lock, unlock } = useScrollLock({ autoLock: false });

  useEffect(() => {
    if (isOpen) lock();
    else unlock();
    return () => unlock();
  }, [isOpen, lock, unlock]);

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className={clsx(s.overlay, s[`pos_${position}`], className)}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          transition={{ duration: 0.2, ease: 'easeOut' }}
        >
          <motion.div
            className={clsx(s.modal, modalClassName)}
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            onClick={(e) => e.stopPropagation()}
          >
            {(title !== null && title !== undefined) || onClose ? (
              <div className={s.header}>
                {title !== null && title !== undefined && (
                  <div className={s.title}>
                    {typeof title === 'string' ? <h3>{title}</h3> : title}
                  </div>
                )}
                {onClose && (
                  <button
                    className={s.closeBtn}
                    type="button"
                    aria-label="Close modal"
                    onClick={onClose}
                  >
                    ×
                  </button>
                )}
              </div>
            ) : null}
            <div className={s.body}>{children}</div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body,
  );
}
