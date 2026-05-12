import { Container, EmptyState, Spinner } from '@/shared/ui';

import { FeedbackForm } from './FeedbackForm';
import { getLocalizedField } from '@/shared/lib';
import s from './ContactsPage.module.scss';
import { useGetContactsQuery } from '@/entities/contacts';
import { useTranslation } from 'react-i18next';

export function ContactsPage() {
  const { i18n, t } = useTranslation();
  const { data, isLoading } = useGetContactsQuery();
  const contactInfo = data
    ? [
        {
          id: 'phone',
          title: t('contacts.phone'),
          primary: data.phone,
          secondary: t('contacts.phoneSecondary'),
          href: `tel:${data.phone.replace(/[^\d+]/g, '')}`,
        },
        {
          id: 'email',
          title: t('contacts.email'),
          primary: data.email,
          secondary: t('contacts.emailSecondary'),
          href: `mailto:${data.email}`,
        },
        {
          id: 'address',
          title: t('contacts.address'),
          primary: getLocalizedField(data, 'address_label', i18n.language),
          secondary: getLocalizedField(data, 'work_hours', i18n.language),
        },
        {
          id: 'hours',
          title: t('contacts.hours'),
          primary: getLocalizedField(data, 'work_hours', i18n.language),
        },
      ]
    : [];

  return (
    <section className={s.page}>
      <Container>
        <h1 className={s.title}>{t('pages.contacts')}</h1>

        {isLoading ? (
          <div className={s.loader}>
            <Spinner size="lg" />
          </div>
        ) : null}

        {!isLoading && !data ? (
          <EmptyState
            className={s.emptyState}
            title={t('common.nothingHere')}
          />
        ) : null}

        {!isLoading && data ? (
          <div className={s.content}>
            <div className={s.leftColumn}>
              <div className={s.infoGrid}>
                {contactInfo.map((item) => (
                  <article className={s.infoItem} key={item.id}>
                    <h2>{item.title}</h2>

                    {item.href ? (
                      <a href={item.href}>{item.primary}</a>
                    ) : (
                      <p>{item.primary}</p>
                    )}

                    {item.secondary ? (
                      <span>
                        {item.secondary.split('\n').map((line) => (
                          <span key={line}>{line}</span>
                        ))}
                      </span>
                    ) : null}
                  </article>
                ))}
              </div>

              {data.address_link ? (
                <div className={s.mapWrap}>
                  <iframe
                    className={s.map}
                    title={t('pages.mapTitle')}
                    src={data.address_link}
                    loading="lazy"
                    referrerPolicy="no-referrer-when-downgrade"
                  />
                </div>
              ) : null}
            </div>

            <FeedbackForm />
          </div>
        ) : null}
      </Container>
    </section>
  );
}
