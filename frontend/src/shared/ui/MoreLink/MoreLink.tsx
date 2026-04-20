import type { ReactNode } from 'react';
import { Link } from 'react-router';

import s from './MoreLink.module.scss';
import { useTranslation } from 'react-i18next';

type MoreLinkProps = {
  to: string;
  children?: ReactNode;
};

export function MoreLink({ to, children }: MoreLinkProps) {
  const { t } = useTranslation();

  return (
    <div className={s.wrapper}>
      <Link className={s.link} to={to}>
        {children ?? t('common.viewMore')}
      </Link>
    </div>
  );
}
