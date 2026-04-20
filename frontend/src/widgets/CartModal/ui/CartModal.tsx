import {
  formatCartPrice,
  removeCartItem,
  selectCartItems,
  selectCartTotalPrice,
  selectCartTotalQuantity,
} from '@/entities/cart';
import { useDispatch, useSelector } from 'react-redux';

import Airplane from '@/shared/assets/icons/airplane.svg';
import { CartItem } from './CartItem';
import { ModalWindowShell } from '@/shared/ui';
import { clearCart } from '@/entities/cart/model/cartSlice';
import s from './CartModal.module.scss';
import { useTranslation } from 'react-i18next';

type CartModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export function CartModal({ isOpen, onClose }: CartModalProps) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const cartItems = useSelector(selectCartItems);
  const totalQuantity = useSelector(selectCartTotalQuantity);
  const totalPrice = useSelector(selectCartTotalPrice);
  const onSubmit = () => {
    dispatch(clearCart());
    onClose();
  };
  return (
    <ModalWindowShell
      className={s.cartModalShell}
      isOpen={isOpen}
      position="top-right"
      title={
        <h2 className={s.title}>
          {t('cart.title')} <span>{totalQuantity}</span> {t('cart.item')}
        </h2>
      }
      onClose={onClose}
    >
      <div className={s.cart}>
        <div className={s.delivery}>
          <img src={Airplane} alt="airplane" />
          <p>
            {t('cart.delivery')} <span>{t('cart.deliveryFrom')}</span>
          </p>
        </div>

        {cartItems.length > 0 ? (
          <div className={s.items}>
            {cartItems.map((item) => (
              <CartItem
                item={item}
                key={item.id}
                quantity={item.quantity}
                onRemove={() => dispatch(removeCartItem(item.id))}
              />
            ))}
          </div>
        ) : (
          <div className={s.empty}>{t('cart.empty')}</div>
        )}

        <div className={s.divider} />

        <div className={s.footer}>
          <div className={s.divider} />
          <div className={s.totalRow}>
            <span>{t('cart.total')}</span>
            <strong>{formatCartPrice(totalPrice)}</strong>
          </div>

          <button className={s.checkoutButton} type="button" onClick={onSubmit}>
            {t('cart.checkout')}
          </button>

          <input
            className={s.promoButton}
            type="text"
            placeholder={t('cart.promo')}
            aria-label={t('cart.promoAria')}
          />
        </div>
      </div>
    </ModalWindowShell>
  );
}
