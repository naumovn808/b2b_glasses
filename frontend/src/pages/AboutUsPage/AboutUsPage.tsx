import { Container } from '@/shared/ui';
import { CertificatesSlider } from './CertificatesSlider';
import brandLogo from '@/shared/assets/image/about/brand.png';
import certificateImage from '@/shared/assets/image/about/certificate.png';
import s from './AboutUsPage.module.scss';
import { useTranslation } from 'react-i18next';

const certificates = [
  {
    id: 'product',
    image: certificateImage,
    title: 'Сертификат на продукцию',
  },
  {
    id: 'conformity',
    image: certificateImage,
    title: 'Сертификат соответствия',
  },
  {
    id: 'expert',
    image: certificateImage,
    title: 'Экспертное заключение',
  },
  {
    id: 'permit',
    image: certificateImage,
    title: 'Разрешительная документация',
  },
];

const partners = Array.from({ length: 18 }, (_, index) => ({
  id: index + 1,
  name: 'Brioni',
  logo: brandLogo,
}));

export function AboutUsPage() {
  const { t } = useTranslation();

  return (
    <section className={s.page}>
      <Container>
        <div className={s.intro}>
          <h1 className={s.title}>{t('nav.about')}</h1>

          <div className={s.introContent}>
            <h2 className={s.lead}>{t('about.lead')}</h2>

            <div className={s.storyList}>
              <article className={s.storyItem}>
                <h3>{t('about.historyTitle')}</h3>
                <p>{t('about.historyText')}</p>
              </article>

              <article className={s.storyItem}>
                <h3>{t('about.missionTitle')}</h3>
                <p>{t('about.missionText')}</p>
              </article>
            </div>
          </div>
        </div>

        <section className={s.certificates}>
          <div className={s.sectionHeader}>
            <h2>{t('about.certificates')}</h2>
            <p>{t('about.certificatesText')}</p>
          </div>

          <CertificatesSlider certificates={certificates} />
        </section>

        <section className={s.partners}>
          <h2>{t('about.partners')}</h2>

          <div className={s.partnerGrid}>
            {partners.map((partner) => (
              <img key={partner.id} src={partner.logo} alt={partner.name} />
            ))}
          </div>
        </section>
      </Container>
    </section>
  );
}
