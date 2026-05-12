import NoPhoto from '@/shared/assets/image/catalog/no-photo.png';
import { QuantityControl } from '@/shared/ui';
import s from './CartItem.module.scss';
import { useTranslation } from 'react-i18next';
export type CartItemData = {
  id: number;
  image?: string;
  oldPrice?: string;
  price: string;
  title: string;
  totalPrice?: string;
  stock: number;
};

type CartItemProps = {
  item: CartItemData;
  isUpdating?: boolean;
  quantity: number;
  onDecrease: () => void;
  onIncrease: () => void;
  onRemove: () => void;
};

export function CartItem({
  isUpdating = false,
  item,
  onDecrease,
  onIncrease,
  onRemove,
  quantity,
}: CartItemProps) {
  const { t } = useTranslation();
  return (
    <div className={s.item}>
      <img
        className={s.itemImage}
        src={item?.image || NoPhoto}
        alt={item.title}
      />
      <div className={s.itemInfo}>
        <div className={s.itemTopLine}>
          <h3>{item.title}</h3>
          <button
            className={s.removeButton}
            type="button"
            aria-label={t('cart.removeItem')}
            onClick={onRemove}
          >
            ×
          </button>
        </div>

        <div className={s.priceRow}>
          <span className={s.price}>{item.price}</span>
          {item.oldPrice ? (
            <span className={s.oldPrice}>{item.oldPrice}</span>
          ) : null}
        </div>

        <div className={s.itemActions}>
          <QuantityControl
            className={s.quantity}
            decreaseDisabled={quantity <= 1 || isUpdating}
            increaseDisabled={quantity >= item.stock}
            disabled={isUpdating}
            isLoading={isUpdating}
            quantity={quantity}
            onDecrease={onDecrease}
            onIncrease={onIncrease}
          />

          <div className={s.stock}>
            <span className={s.stockText}>
              {item.stock !== undefined
                ? t('common.inStockCount', { count: item.stock })
                : t('common.inStock')}
            </span>
            <span className={s.stockBar} />
          </div>
        </div>
      </div>
    </div>
  );
}
