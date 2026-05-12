import { Spinner } from '../Spinner';
import clsx from 'clsx';
import s from './QuantityControl.module.scss';
import { useTranslation } from 'react-i18next';

type QuantityControlProps = {
  quantity: number;
  className?: string;
  disabled?: boolean;
  decreaseDisabled?: boolean;
  increaseDisabled?: boolean;
  isLoading?: boolean;
  onDecrease: () => void;
  onIncrease: () => void;
};

export function QuantityControl({
  className,
  decreaseDisabled,
  disabled = false,
  increaseDisabled,
  isLoading = false,
  onDecrease,
  onIncrease,
  quantity,
}: QuantityControlProps) {
  const { t } = useTranslation();

  return (
    <div
      className={clsx(s.quantity, className)}
      aria-label={t('common.quantity')}
    >
      <button
        type="button"
        disabled={disabled || decreaseDisabled}
        onClick={onDecrease}
        aria-label={t('common.remove')}
      >
        -
      </button>
      <span>{isLoading ? <Spinner size="sm" /> : quantity}</span>
      <button
        type="button"
        disabled={disabled || increaseDisabled}
        onClick={onIncrease}
        aria-label={t('common.add')}
      >
        +
      </button>
    </div>
  );
}
