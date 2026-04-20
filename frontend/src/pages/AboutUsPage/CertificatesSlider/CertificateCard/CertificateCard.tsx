import EyeIcon from '@/shared/assets/icons/eye.svg?react';

import s from './CertificateCard.module.scss';
import { useTranslation } from 'react-i18next';

export type CertificateCardData = {
  id: string;
  image: string;
  title: string;
};

type CertificateCardProps = {
  certificate: CertificateCardData;
  onView: (certificate: CertificateCardData) => void;
};

export function CertificateCard({ certificate, onView }: CertificateCardProps) {
  const { t } = useTranslation();
  const title = t(`certificates.${certificate.id}`, certificate.title);

  return (
    <article className={s.certificateCard}>
      <img src={certificate.image} alt={title} />

      <div className={s.certificateOverlay}>
        <span>{title}</span>
      </div>

      <button
        className={s.viewButton}
        type="button"
        onClick={() => onView(certificate)}
      >
        <EyeIcon aria-hidden="true" />
        {t('certificates.view')}
      </button>
    </article>
  );
}
