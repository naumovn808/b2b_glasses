import { MoreLink, SectionContainer } from '@/shared/ui';
import { EducationCard } from './EducationCard/EducationCard';
import { educationItems } from '../model/educationContent';
import s from './EducationPage.module.scss';
import { useTranslation } from 'react-i18next';

export function EducationPage() {
  const { t } = useTranslation();

  return (
    <SectionContainer
      title={t('pages.education')}
      className={s.section}
      innerClassName={s.sectionInner}
      headingClassName={s.heading}
    >
      <div className={s.grid}>
        {educationItems.map((item) => (
          <EducationCard key={item.id} item={item} />
        ))}
      </div>

      <MoreLink to={`/education/${educationItems[0]?.slug ?? ''}`} />
    </SectionContainer>
  );
}
