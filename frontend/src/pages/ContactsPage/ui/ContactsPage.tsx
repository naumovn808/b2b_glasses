import { Container } from '@/shared/ui';
import { FeedbackForm } from './FeedbackForm';
import { contactInfo, yandexMapUrl } from '../model/contactContent';
import s from './ContactsPage.module.scss';
import { useTranslation } from 'react-i18next';

export function ContactsPage() {
  const { t } = useTranslation();

  return (
    <section className={s.page}>
      <Container>
        <h1 className={s.title}>{t('pages.contacts')}</h1>

        <div className={s.content}>
          <div className={s.leftColumn}>
            <div className={s.infoGrid}>
              {contactInfo.map((item) => (
                <article className={s.infoItem} key={item.id}>
                  <h2>{t(`contacts.${item.id}`, item.title)}</h2>

                  {item.href ? (
                    <a href={item.href}>
                      {t(`contacts.${item.id}Primary`, item.primary)}
                    </a>
                  ) : (
                    <p>{t(`contacts.${item.id}Primary`, item.primary)}</p>
                  )}

                  {item.secondary ? (
                    <span>
                      {t(`contacts.${item.id}Secondary`, item.secondary)
                        .split('\n')
                        .map((line) => (
                        <span key={line}>{line}</span>
                        ))}
                    </span>
                  ) : null}
                </article>
              ))}
            </div>

            <div className={s.mapWrap}>
              <iframe
                className={s.map}
                title={t('pages.mapTitle')}
                src={yandexMapUrl}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            </div>
          </div>

          <FeedbackForm />
        </div>
      </Container>
    </section>
  );
}
