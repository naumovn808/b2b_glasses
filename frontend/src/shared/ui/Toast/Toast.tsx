import { motion } from 'framer-motion';
import { useEffect } from 'react';

import clsx from 'clsx';
import s from './Toast.module.scss';

type ToastProps = {
  message: string;
  type?: 'success' | 'error';
  duration?: number;
  onClose: () => void;
};

export function Toast({ message, type = 'success', duration = 3000, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 100, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
      className={clsx(s.toast, s[type])}
    >
      <div className={s.content}>{message}</div>
      <button className={s.closeButton} onClick={onClose} aria-label="Close">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13.5 4.5L4.5 13.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M4.5 4.5L13.5 13.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </motion.div>
  );
}

// Контейнер для нескольких уведомлений (если нужно в будущем)
export function ToastContainer({ children }: { children: React.ReactNode }) {
  return <div className={s.toastContainer}>{children}</div>;
}
