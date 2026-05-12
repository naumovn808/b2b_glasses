import { Container, EmptyState, RichText, Spinner } from '@/shared/ui';

import { CertificatesSlider } from './CertificatesSlider';
import { getLocalizedField } from '@/shared/lib';
import s from './AboutUsPage.module.scss';
import { useGetAboutQuery } from '@/entities/about';
import { useTranslation } from 'react-i18next';

export function AboutUsPage() {
  const { i18n, t } = useTranslation();
  const { data, isLoading } = useGetAboutQuery();
  const certificates =
    data?.certificates.map((certificate) => ({
      id: String(certificate.id),
      image: certificate.image,
      title: certificate.title ?? '',
    })) ?? [];
  const partners = data?.partners ?? [];
  const title = data ? getLocalizedField(data, 'title', i18n.language) : '';

  return (
    <section className={s.page}>
      <Container>
        {isLoading ? (
          <div className={s.loader}>
            <Spinner size="lg" />
          </div>
        ) : null}

        {!isLoading && !data ? (
          <EmptyState title={t('common.nothingHere')} />
        ) : null}

        {!isLoading && data ? (
          <>
            <div className={s.intro}>
              <h1 className={s.title}>{t('nav.about')}</h1>

              <div className={s.introContent}>
                <h2 className={s.lead}>{title}</h2>
                <RichText className={s.introRichText} html={data.text} />
              </div>
            </div>

            {certificates.length > 0 ? (
              <section className={s.certificates}>
                <div className={s.sectionHeader}>
                  <h2>{t('about.certificates')}</h2>
                  <p>{t('about.certificatesText')}</p>
                </div>

                <CertificatesSlider certificates={certificates} />
              </section>
            ) : null}

            {partners.length > 0 ? (
              <section className={s.partners}>
                <h2>{t('about.partners')}</h2>

                <div className={s.partnerGrid}>
                  {partners.map((partner) => {
                    const image = (
                      <img
                        src={partner.image}
                        alt={partner.name ?? ''}
                        loading="lazy"
                      />
                    );

                    return partner.link ? (
                      <a
                        key={partner.id}
                        href={partner.link}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {image}
                      </a>
                    ) : (
                      <span key={partner.id}>{image}</span>
                    );
                  })}
                </div>
              </section>
            ) : null}
          </>
        ) : null}
      </Container>
    </section>
  );
}
