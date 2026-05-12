import clsx from 'clsx';
import s from './Spinner.module.scss';

type SpinnerProps = {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
};

export function Spinner({ className, size = 'md' }: SpinnerProps) {
  return (
    <span
      className={clsx(s.spinner, s[size], className)}
      role="status"
      aria-label="Loading"
    />
  );
}
