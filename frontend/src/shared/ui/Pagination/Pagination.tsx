import clsx from 'clsx';
import s from './Pagination.module.scss';
import { useTranslation } from 'react-i18next';

type PaginationProps = {
  currentPage: number;
  totalPages: number;
  className?: string;
  onPageChange: (page: number) => void;
};

type PaginationItem = number | 'dots';

function getPaginationItems(
  currentPage: number,
  totalPages: number,
): PaginationItem[] {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, index) => index + 1);
  }

  const items: PaginationItem[] = [];

  const showLeftDots = currentPage > 4;
  const showRightDots = currentPage < totalPages - 3;

  items.push(1);

  if (showLeftDots) {
    items.push('dots');
  }

  const startPage = Math.max(2, currentPage - 1);
  const endPage = Math.min(totalPages - 1, currentPage + 1);

  for (let page = startPage; page <= endPage; page += 1) {
    items.push(page);
  }

  if (showRightDots) {
    items.push('dots');
  }

  items.push(totalPages);

  return items;
}

export function Pagination({
  className,
  currentPage,
  onPageChange,
  totalPages,
}: PaginationProps) {
  const { t } = useTranslation();

  const pages = getPaginationItems(currentPage, totalPages);

  const canGoPrev = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  if (totalPages <= 1) {
    return null;
  }

  return (
    <nav
      className={clsx(s.pagination, className)}
      aria-label={t('pagination.label')}
    >
      <button
        className={clsx(s.navButton, !canGoPrev && s.disabled)}
        type="button"
        disabled={!canGoPrev}
        aria-label={t('pagination.prev')}
        onClick={() => onPageChange(currentPage - 1)}
      >
        ‹
      </button>

      {pages.map((page, index) => {
        if (page === 'dots') {
          return (
            <span className={s.dots} key={`dots-${index}`}>
              ...
            </span>
          );
        }

        return (
          <button
            className={clsx(s.pageButton, page === currentPage && s.pageActive)}
            key={page}
            type="button"
            aria-current={page === currentPage ? 'page' : undefined}
            onClick={() => onPageChange(page)}
          >
            {page}
          </button>
        );
      })}

      <button
        className={clsx(s.navButton, !canGoNext && s.disabled)}
        type="button"
        disabled={!canGoNext}
        aria-label={t('pagination.next')}
        onClick={() => onPageChange(currentPage + 1)}
      >
        ›
      </button>
    </nav>
  );
}
