import { AnimatePresence, motion } from 'framer-motion';
import { createPortal } from 'react-dom';
import { useEffect } from 'react';

import type { CertificateCardData } from '../CertificateCard';
import s from './CertificateImageModal.module.scss';
import { useTranslation } from 'react-i18next';

type CertificateImageModalProps = {
  certificate: CertificateCardData | null;
  onClose: () => void;
};

export function CertificateImageModal({
  certificate,
  onClose,
}: CertificateImageModalProps) {
  const { t } = useTranslation();
  const title = certificate
    ? t(`certificates.${certificate.id}`, certificate.title)
    : '';

  useEffect(() => {
    if (!certificate) {
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [certificate, onClose]);

  return createPortal(
    <AnimatePresence>
      {certificate ? (
        <motion.div
          className={s.overlay}
          role="dialog"
          aria-modal="true"
          aria-label={title}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          onMouseDown={(event) => {
            if (event.currentTarget === event.target) {
              onClose();
            }
          }}
        >
          <motion.div
            className={s.content}
            initial={{ opacity: 0, y: 14, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 14, scale: 0.98 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
          >
            <img
              className={s.image}
              src={certificate.image}
              alt={title}
            />
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>,
    document.body,
  );
}
