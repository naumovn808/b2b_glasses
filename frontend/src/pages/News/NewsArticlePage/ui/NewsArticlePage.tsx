import { EmptyState, RichText, Spinner } from '@/shared/ui';

import { getLocalizedField } from '@/shared/lib';
import s from './NewsArticlePage.module.scss';
import { useGetNewsByIdQuery } from '@/entities/news';
import { useParams } from 'react-router';
import { useTranslation } from 'react-i18next';

export function NewsArticlePage() {
  const { i18n, t } = useTranslation();
  const { newsId } = useParams();
  const {
    data: article,
    isError,
    isLoading,
  } = useGetNewsByIdQuery(newsId ?? '', {
    skip: !newsId,
  });

  if (isLoading) {
    return (
      <section className={s.section}>
        <Spinner size="lg" />
      </section>
    );
  }

  if (isError || !article) {
    return (
      <section className={s.section}>
        <EmptyState title={t('common.notFound')} />
      </section>
    );
  }

  const title = getLocalizedField(article, 'title', i18n.language);
  const text = getLocalizedField(article, 'text', i18n.language);

  return (
    <section className={s.section}>
      {/* <Container className={s.sectionContainer}> */}
      <div className={s.layout}>
        <div className={s.mediaColumn}>
          <picture>
            <img className={s.media} src={article.image} alt={title} />
          </picture>
        </div>

        <article className={s.content}>
          <h1 className={s.headline}>{title}</h1>

          <div className={s.sections}>
            <section className={s.articleSection}>
              <h2 className={s.sectionTitle}>{title}</h2>
              <RichText className={s.sectionText} html={text} />
            </section>
          </div>
        </article>
      </div>
      {/* </Container> */}
    </section>
  );
}
