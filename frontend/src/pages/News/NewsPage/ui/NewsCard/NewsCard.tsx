import ArrowIcon from '@/shared/assets/icons/arrow.svg?react';
import { Link } from 'react-router';
import type { NewsCard as NewsCardType } from '../../model/newsCards';
import s from './NewsCard.module.scss';
import { useTranslation } from 'react-i18next';

type NewsCardProps = {
  card: NewsCardType;
};

export function NewsCard({ card }: NewsCardProps) {
  const { t } = useTranslation();
  const title = t('news.cardTitle', card.title);

  return (
    <Link className={`${s.card}`} to={card.href}>
      <img
        className={s.media}
        src={card.image}
        alt={title}
        loading="lazy"
      />

      <div className={s.content}>
        <p className={s.title}>{title}</p>

        <span className={s.arrowBadge} aria-hidden="true">
          <ArrowIcon />
        </span>
      </div>
    </Link>
  );
}
