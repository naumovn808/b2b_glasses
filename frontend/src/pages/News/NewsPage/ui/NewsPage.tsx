import { EmptyState, SectionContainer, Spinner } from '@/shared/ui';
import { NewsCard } from './NewsCard/NewsCard';
import { getLocalizedField } from '@/shared/lib';
import s from './NewsPage.module.scss';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useGetNewsQuery } from '@/entities/news';

const INITIAL_VISIBLE_ITEMS = 4;

export function NewsPage() {
  const { i18n, t } = useTranslation();
  const [visibleItemsCount, setVisibleItemsCount] = useState(
    INITIAL_VISIBLE_ITEMS,
  );
  const { data, isLoading } = useGetNewsQuery();
  const newsItems = useMemo(
    () =>
      data?.results.map((news) => ({
        id: news.id,
        title: getLocalizedField(news, 'title', i18n.language),
        href: `/news/${news.id}`,
        image: news.image,
      })) ?? [],
    [data?.results, i18n.language],
  );
  const visibleNewsItems = newsItems.slice(0, visibleItemsCount);
  const canShowMore = visibleItemsCount < newsItems.length;

  return (
    <SectionContainer
      title={t('pages.news')}
      innerClassName={s.sectionInner}
      headingClassName={s.heading}
    >
      {isLoading ? (
        <div className={s.loader}>
          <Spinner size="lg" />
        </div>
      ) : newsItems.length === 0 ? (
        <EmptyState title={t('common.nothingHere')} />
      ) : (
        <div className={s.grid}>
          {visibleNewsItems.map((card) => (
            <NewsCard key={card.id} card={card} />
          ))}
        </div>
      )}

      {!isLoading && canShowMore ? (
        <div className={s.moreButtonWrap}>
          <button
            className={s.moreButton}
            type="button"
            onClick={() =>
              setVisibleItemsCount((count) =>
                Math.min(count + INITIAL_VISIBLE_ITEMS, newsItems.length),
              )
            }
          >
            {t('common.viewMore')}
          </button>
        </div>
      ) : null}
    </SectionContainer>
  );
}
