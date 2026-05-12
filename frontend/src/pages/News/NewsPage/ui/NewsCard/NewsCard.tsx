import ArrowIcon from '@/shared/assets/icons/arrow.svg?react';
import { Link } from 'react-router';
import s from './NewsCard.module.scss';

export type NewsCardItem = {
  id: number;
  title: string;
  href: string;
  image: string;
};

type NewsCardProps = {
  card: NewsCardItem;
};

export function NewsCard({ card }: NewsCardProps) {
  return (
    <Link className={`${s.card}`} to={card.href}>
      <img
        className={s.media}
        src={card.image}
        alt={card.title}
        loading="lazy"
      />

      <div className={s.content}>
        <p className={s.title}>{card.title}</p>

        <span className={s.arrowBadge} aria-hidden="true">
          <ArrowIcon />
        </span>
      </div>
    </Link>
  );
}
