import type { CartItem } from './types';

export type CartRootState = {
  cart: {
    items: CartItem[];
  };
};

function getPriceValue(price: string) {
  const normalizedPrice = price.replace(',', '.').replace(/[^\d.]/g, '');

  return Number(normalizedPrice) || 0;
}

export function selectCartItems(state: CartRootState) {
  return state.cart.items;
}

export function selectCartTotalQuantity(state: CartRootState) {
  return state.cart.items.reduce((total, item) => total + item.quantity, 0);
}

export function selectCartTotalPrice(state: CartRootState) {
  return state.cart.items.reduce(
    (total, item) => total + getPriceValue(item.price) * item.quantity,
    0,
  );
}

export function selectCartItemById(state: CartRootState, itemId: string) {
  return state.cart.items.find((item) => item.id === itemId);
}

export function formatCartPrice(price: number) {
  return `${price.toFixed(2)}Р`;
}
