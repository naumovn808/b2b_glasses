import { CartQuantityControl } from '@/features/cart-quantity-control';
import s from './CartItem.module.scss';
import { useTranslation } from 'react-i18next';

export type CartItemData = {
  id: string;
  color: string;
  colorId?: string;
  image: string;
  oldPrice?: string;
  price: string;
  size: string;
  stockText: string;
  title: string;
};

type CartItemProps = {
  item: CartItemData;
  quantity: number;
  onRemove: () => void;
};

export function CartItem({
  item,
  onRemove,
  quantity,
}: CartItemProps) {
  const { t } = useTranslation();

  return (
    <div className={s.item}>
      <img className={s.itemImage} src={item.image} alt={item.title} />

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

        <div className={s.meta}>
          <span>
            {t('common.color')}:{' '}
            {item.colorId
              ? t(`catalog.option.${item.colorId}`, item.color)
              : item.color}
          </span>
          <span>
            {t('common.size')}: {item.size}
          </span>
        </div>

        <div className={s.priceRow}>
          <span className={s.price}>{item.price}</span>
          {item.oldPrice ? (
            <span className={s.oldPrice}>{item.oldPrice}</span>
          ) : null}
        </div>

        <div className={s.itemActions}>
          <CartQuantityControl
            className={s.quantity}
            itemId={item.id}
            quantity={quantity}
          />

          <div className={s.stock}>
            <span className={s.stockText}>{t('common.inStockCount')}</span>
            <span className={s.stockBar} />
          </div>
        </div>
      </div>
    </div>
  );
}
