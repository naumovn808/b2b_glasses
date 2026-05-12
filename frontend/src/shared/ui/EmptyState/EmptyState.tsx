import clsx from 'clsx';
import s from './EmptyState.module.scss';

type EmptyStateProps = {
  className?: string;
  title: string;
};

export function EmptyState({ className, title }: EmptyStateProps) {
  return (
    <div className={clsx(s.root, className)}>
      <p>{title}</p>
    </div>
  );
}
