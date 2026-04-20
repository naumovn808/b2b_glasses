import ArrowIcon from '@/shared/assets/icons/arrow.svg?react';
import type { EducationItem } from '../../model/educationContent';
import { Link } from 'react-router';
import s from './EducationCard.module.scss';
import { useTranslation } from 'react-i18next';

type EducationCardProps = {
  item: EducationItem;
};

export function EducationCard({ item }: EducationCardProps) {
  const { t } = useTranslation();
  const title = t(
    item.id % 2 === 0 ? 'education.crizal' : 'education.chooseIndex',
    item.title,
  );

  return (
    <Link className={s.card} to={`/education/${item.slug}`}>
      <img
        className={s.media}
        src={item.image}
        alt={title}
        loading="lazy"
      />

      <div className={s.content}>
        <span className={s.title}>{title}</span>

        <span className={s.iconWrap} aria-hidden="true">
          <ArrowIcon />
        </span>
      </div>
    </Link>
  );
}
