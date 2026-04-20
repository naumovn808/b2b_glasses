import { configureStore } from '@reduxjs/toolkit';
import { cartReducer } from '@/entities/cart';
import { userReducer } from '@/entities/user';

export const store = configureStore({
  reducer: {
    cart: cartReducer,
    user: userReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
