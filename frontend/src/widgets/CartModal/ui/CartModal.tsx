import { EmptyState, ModalWindowShell, Spinner, Toast, ToastContainer } from '@/shared/ui';
import { AnimatePresence } from 'framer-motion';
import {
  clearLocalCart,
  useCheckoutCartMutation,
  useClearCartMutation,
  useDeleteCartItemMutation,
  useGetCartQuery,
  usePartialUpdateCartItemMutation,
} from '@/entities/cart';
import { useDispatch, useSelector } from 'react-redux';

import Airplane from '@/shared/assets/icons/airplane.svg';
import { CartItem } from './CartItem';
import s from './CartModal.module.scss';
import { selectUserToken } from '@/entities/user';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

type CartModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

function formatServerCartPrice(price?: string) {
  return price ? `$${price}` : '$0.00';
}

function extractApiErrorMessage(error: unknown, fallback: string): string {
  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as { data?: unknown }).data;
    if (data && typeof data === 'object') {
      const record = data as Record<string, unknown>;
      if (typeof record.message === 'string' && record.message.trim()) {
        return record.message;
      }
      if (typeof record.error === 'string' && record.error.trim()) {
        return record.error;
      }
      if (typeof record.detail === 'string' && record.detail.trim()) {
        return record.detail;
      }
      const qty = record.quantity;
      if (Array.isArray(qty) && typeof qty[0] === 'string') {
        return qty[0];
      }
      if (typeof qty === 'string' && qty.trim()) {
        return qty;
      }
    }
  }
  return fallback;
}

export function CartModal({ isOpen, onClose }: CartModalProps) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const token = useSelector(selectUserToken);
  const [updatingItems, setUpdatingItems] = useState<Set<number>>(new Set());
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const {
    data: cart,
    isFetching,
    refetch: refetchCart,
  } = useGetCartQuery(undefined, {
    skip: !token,
  });
  const [checkoutCart, { isLoading: isCheckoutLoading }] =
    useCheckoutCartMutation();
  const [clearCart, { isLoading: isClearLoading }] = useClearCartMutation();
  const [deleteCartItem, { isLoading: isDeleteLoading }] =
    useDeleteCartItemMutation();
  const [partialUpdateCartItem, { isLoading: isUpdateLoading }] =
    usePartialUpdateCartItemMutation();
  const cartItems = cart?.items ?? [];
  const totalQuantity = cartItems.reduce(
    (total, item) => total + (item.quantity ?? 1),
    0,
  );
  const totalPrice = cartItems.reduce((sum, item) => {
    const price = parseFloat(item.total_price?.replace(/[^\d.]/g, '') || '0');
    return sum + price;
  }, 0);
  const isCartUpdating =
    isCheckoutLoading || isClearLoading || isDeleteLoading || isUpdateLoading;

  const handleCheckout = async () => {
    try {
      const result = await checkoutCart().unwrap();
      dispatch(clearLocalCart());
      const successMsg = result?.doc_number_1c
        ? `${t('cart.checkoutSuccess')} (${result.doc_number_1c})`
        : t('cart.checkoutSuccess');
      setToast({ message: successMsg, type: 'success' });
      onClose();
    } catch (error) {
      const errorMessage = extractApiErrorMessage(
        error,
        'Не удалось оформить заказ. Попробуйте позже.',
      );
      setToast({ message: errorMessage, type: 'error' });
      void refetchCart();
    }
  };

  const handleClearCart = async () => {
    try {
      await clearCart().unwrap();
      dispatch(clearLocalCart());
      setToast({ message: t('cart.clearSuccess'), type: 'success' });
    } catch (error) {
      setToast({
        message: extractApiErrorMessage(error, 'Не удалось очистить корзину.'),
        type: 'error',
      });
    }
  };

  const handleQuantityChange = async (itemId: number, quantity: number) => {
    setUpdatingItems((prev) => new Set(prev).add(itemId));
    try {
      await partialUpdateCartItem({
        id: itemId,
        data: { quantity },
      }).unwrap();
    } catch (error) {
      setToast({
        message: extractApiErrorMessage(
          error,
          'Не удалось обновить количество товара.',
        ),
        type: 'error',
      });
      void refetchCart();
    } finally {
      setUpdatingItems((prev) => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  const handleDeleteCartItem = async (itemId: number) => {
    setUpdatingItems((prev) => new Set(prev).add(itemId));
    try {
      await deleteCartItem(itemId).unwrap();
    } catch (error) {
      setToast({
        message: extractApiErrorMessage(error, 'Не удалось удалить позицию.'),
        type: 'error',
      });
    } finally {
      setUpdatingItems((prev) => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  return (
    <>
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

        {/* {isFetching ? (
        //   <div className={s.loader}>
        //     <Spinner size="md" />
        //   </div>
        // ) : null} */}

        {/* {!isFetching && isCartUpdating ? (
          <div className={s.loader}>
            <Spinner size="sm" />
          </div>
        ) : null} */}

        {cartItems.length > 0 ? (
          <div className={s.items}>
            {cartItems.map((item) => (
              <CartItem
                item={{
                  id: item.id,
                  image: item.image,
                  price: formatServerCartPrice(item.price_at_order),
                  title: item.product,
                  totalPrice: formatServerCartPrice(item.total_price),
                  stock: item.stock,
                }}
                isUpdating={updatingItems.has(item.id)}
                key={item.id}
                quantity={item.quantity ?? 1}
                onDecrease={() =>
                  handleQuantityChange(
                    item.id,
                    Math.max(1, (item.quantity ?? 1) - 1),
                  )
                }
                onIncrease={() =>
                  handleQuantityChange(item.id, (item.quantity ?? 1) + 1)
                }
                onRemove={() => handleDeleteCartItem(item.id)}
              />
            ))}
          </div>
        ) : null}

        {!isFetching && cartItems.length === 0 ? (
          <EmptyState className={s.empty} title={t('cart.empty')} />
        ) : null}

        <div className={s.divider} />

        <div className={s.footer}>
          <div className={s.divider} />
          <div className={s.totalRow}>
            <span>{t('cart.total')}</span>
            <strong>{formatServerCartPrice(totalPrice.toString())}</strong>
          </div>

          <button
            className={s.checkoutButton}
            type="button"
            disabled={cartItems.length === 0 || isCartUpdating}
            onClick={handleCheckout}
          >
            {isCheckoutLoading ? <Spinner size="sm" /> : t('cart.checkout')}
          </button>

          <button
            className={s.promoButton}
            type="button"
            disabled={cartItems.length === 0 || isCartUpdating}
            onClick={handleClearCart}
          >
            {isClearLoading ? <Spinner size="sm" /> : t('cart.clear')}
          </button>
        </div>
      </div>
    </ModalWindowShell>
    <ToastContainer>
      <AnimatePresence>
        {toast && (
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        )}
      </AnimatePresence>
    </ToastContainer>
    </>
  );
}
