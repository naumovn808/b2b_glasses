import { EmptyState, SectionContainer, Spinner } from '@/shared/ui';
import { useMemo, useState } from 'react';

import { EducationCard } from './EducationCard/EducationCard';
import { getLocalizedField } from '@/shared/lib';
import s from './EducationPage.module.scss';
import { useGetTrainingQuery } from '@/entities/training';
import { useTranslation } from 'react-i18next';

const INITIAL_VISIBLE_ITEMS = 4;

export function EducationPage() {
  const { i18n, t } = useTranslation();
  const [visibleItemsCount, setVisibleItemsCount] = useState(
    INITIAL_VISIBLE_ITEMS,
  );
  const { data, isLoading } = useGetTrainingQuery();
  const trainingItems = useMemo(
    () =>
      data?.results.map((training) => ({
        id: training.id,
        image: training.image,
        video: training.video,
        slug: String(training.id),
        title: getLocalizedField(training, 'title', i18n.language),
      })) ?? [],
    [data?.results, i18n.language],
  );
  const visibleTrainingItems = trainingItems.slice(0, visibleItemsCount);
  const canShowMore = visibleItemsCount < trainingItems.length;

  return (
    <SectionContainer
      title={t('pages.education')}
      className={s.section}
      innerClassName={s.sectionInner}
      headingClassName={s.heading}
    >
      {isLoading ? (
        <div className={s.loader}>
          <Spinner size="lg" />
        </div>
      ) : trainingItems.length === 0 ? (
        <EmptyState title={t('common.nothingHere')} />
      ) : (
        <div className={s.grid}>
          {visibleTrainingItems.map((item) => (
            <EducationCard key={item.id} item={item} />
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
                Math.min(count + INITIAL_VISIBLE_ITEMS, trainingItems.length),
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
