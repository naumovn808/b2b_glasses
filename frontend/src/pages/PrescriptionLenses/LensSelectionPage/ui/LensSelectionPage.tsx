import { Link } from 'react-router';

import { Container } from '@/shared/ui';
import { LensSelectionForm } from './LensSelectionForm';
import s from './LensSelectionPage.module.scss';
import { useTranslation } from 'react-i18next';

export function LensSelectionPage() {
  const { t } = useTranslation();

  return (
    <section className={s.page}>
      <Container>
        <div className={s.inner}>
          <header className={s.header}>
            <Link
              className={s.backLink}
              to="/prescription-lenses"
              aria-label={t('prescription.backToOrder')}
            >
              ←
            </Link>
            <h1>{t('prescription.lensSelection')}</h1>
          </header>

          <LensSelectionForm />
        </div>
      </Container>
    </section>
  );
}
