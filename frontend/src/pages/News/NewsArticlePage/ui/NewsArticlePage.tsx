import { Navigate, useParams } from 'react-router';

import { getNewsCardById } from '@/pages/News/NewsPage/model/newsCards';
import s from './NewsArticlePage.module.scss';
import { useTranslation } from 'react-i18next';

const sectionTitleKeys = [
  ['news.historyTitle', 'news.missionTitle'],
  ['news.collectionsTitle', 'news.clientTitle'],
  ['news.materialsTitle', 'news.qualityTitle'],
  ['news.navigationTitle', 'news.whyTitle'],
];

export function NewsArticlePage() {
  const { t } = useTranslation();
  const { newsId } = useParams();
  const articleId = Number(newsId);
  const article = Number.isNaN(articleId)
    ? undefined
    : getNewsCardById(articleId);

  if (!article) {
    return <Navigate replace to="/news" />;
  }

  const headline = t(`news.headline${article.id}`, article.headline);
  const translatedSectionTitleKeys = sectionTitleKeys[article.id - 1] ?? [];

  return (
    <section className={s.section}>
      {/* <Container className={s.sectionContainer}> */}
      <div className={s.layout}>
        <div className={s.mediaColumn}>
          <picture>
            {article.mobileImage ? (
              <source media="(max-width: 900px)" srcSet={article.mobileImage} />
            ) : null}
            <img className={s.media} src={article.image} alt={headline} />
          </picture>
        </div>

        <article className={s.content}>
          <h1 className={s.headline}>{headline}</h1>

          <div className={s.sections}>
            {article.sections.map((section, index) => (
              <section key={section.title} className={s.articleSection}>
                <h2 className={s.sectionTitle}>
                  {t(translatedSectionTitleKeys[index] ?? section.title, section.title)}
                </h2>
                <p className={s.sectionText}>{section.text}</p>
              </section>
            ))}
          </div>
        </article>
      </div>
      {/* </Container> */}
    </section>
  );
}
