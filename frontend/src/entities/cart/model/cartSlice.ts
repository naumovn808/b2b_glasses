import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

import type { AddCartItemPayload, CartItem } from './types';

type CartState = {
  items: CartItem[];
};

const initialState: CartState = {
  items: [],
};

export function makeCartItemId(item: AddCartItemPayload) {
  return [item.productId, item.colorId ?? item.color, item.size].join('__');
}

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    addCartItem(state, action: PayloadAction<AddCartItemPayload>) {
      const id = makeCartItemId(action.payload);
      const existingItem = state.items.find((item) => item.id === id);

      if (existingItem) {
        existingItem.quantity += action.payload.quantity;
        return;
      }

      state.items.push({
        ...action.payload,
        id,
      });
    },
    decrementCartItem(state, action: PayloadAction<string>) {
      const item = state.items.find(
        (cartItem) => cartItem.id === action.payload,
      );

      if (!item) return;

      item.quantity = Math.max(1, item.quantity - 1);
    },
    incrementCartItem(state, action: PayloadAction<string>) {
      const item = state.items.find(
        (cartItem) => cartItem.id === action.payload,
      );

      if (!item) return;

      item.quantity += 1;
    },
    removeCartItem(state, action: PayloadAction<string>) {
      state.items = state.items.filter((item) => item.id !== action.payload);
    },
    clearCart(state) {
      state.items = [];
    },
  },
});

export const {
  addCartItem,
  decrementCartItem,
  clearCart,
  incrementCartItem,
  removeCartItem,
} = cartSlice.actions;

export const cartReducer = cartSlice.reducer;
