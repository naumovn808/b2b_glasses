import clsx from 'clsx';
import s from './Pagination.module.scss';
import { useTranslation } from 'react-i18next';

type PaginationProps = {
  currentPage: number;
  totalPages: number;
  className?: string;
  onPageChange: (page: number) => void;
};

function getPaginationItems(totalPages: number) {
  return Array.from({ length: totalPages }, (_, index) => index + 1);
}

export function Pagination({
  className,
  currentPage,
  onPageChange,
  totalPages,
}: PaginationProps) {
  const { t } = useTranslation();
  const pages = getPaginationItems(totalPages);
  const canGoNext = currentPage < totalPages;

  return (
    <nav className={clsx(s.pagination, className)} aria-label={t('pagination.label')}>
      {pages.map((page) => (
        <button
          className={clsx(s.pageButton, page === currentPage && s.pageActive)}
          key={page}
          type="button"
          aria-current={page === currentPage ? 'page' : undefined}
          onClick={() => onPageChange(page)}
        >
          {page}
        </button>
      ))}

      <button
        className={s.navButton}
        type="button"
        disabled={!canGoNext}
        aria-label={t('pagination.next')}
        onClick={() => onPageChange(currentPage + 1)}
      >
        »
      </button>
    </nav>
  );
}
