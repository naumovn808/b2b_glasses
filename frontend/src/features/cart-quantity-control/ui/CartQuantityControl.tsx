import {
  decrementCartItem,
  incrementCartItem,
} from '@/entities/cart';
import { QuantityControl } from '@/shared/ui';
import { useDispatch } from 'react-redux';

type CartQuantityControlProps = {
  itemId: string;
  quantity: number;
  className?: string;
  disabled?: boolean;
};

export function CartQuantityControl({
  className,
  disabled = false,
  itemId,
  quantity,
}: CartQuantityControlProps) {
  const dispatch = useDispatch();

  return (
    <QuantityControl
      className={className}
      decreaseDisabled={quantity <= 1}
      disabled={disabled}
      quantity={quantity}
      onDecrease={() => dispatch(decrementCartItem(itemId))}
      onIncrease={() => dispatch(incrementCartItem(itemId))}
    />
  );
}
