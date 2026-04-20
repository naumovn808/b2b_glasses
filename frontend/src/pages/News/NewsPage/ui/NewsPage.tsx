import { MoreLink, SectionContainer } from '@/shared/ui';
import { NewsCard } from './NewsCard/NewsCard';
import { newsCards } from '../model/newsCards';
import s from './NewsPage.module.scss';
import { useTranslation } from 'react-i18next';

export function NewsPage() {
  const { t } = useTranslation();

  return (
    <SectionContainer
      title={t('pages.news')}
      innerClassName={s.sectionInner}
      headingClassName={s.heading}
    >
      <div className={s.grid}>
        {newsCards.map((card) => (
          <NewsCard key={card.id} card={card} />
        ))}
      </div>

      <MoreLink to="/news" />
    </SectionContainer>
  );
}
