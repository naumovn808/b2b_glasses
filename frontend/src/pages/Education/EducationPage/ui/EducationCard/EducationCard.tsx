import ArrowIcon from '@/shared/assets/icons/arrow.svg?react';
import { Link } from 'react-router';
import s from './EducationCard.module.scss';

type EducationItem = {
  id: number;
  image: string;
  slug: string;
  title: string;
};

type EducationCardProps = {
  item: EducationItem;
};

export function EducationCard({ item }: EducationCardProps) {
  return (
    <Link className={s.card} to={`/education/${item.slug}`}>
      <img
        className={s.media}
        src={item.image}
        alt={item.title}
        loading="lazy"
      />
      <div className={s.content}>
        <span className={s.title}>{item.title}</span>

        <span className={s.iconWrap} aria-hidden="true">
          <ArrowIcon />
        </span>
      </div>
    </Link>
  );
}
