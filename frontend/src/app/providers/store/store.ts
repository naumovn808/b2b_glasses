import { configureStore } from '@reduxjs/toolkit';
import { cartReducer } from '@/entities/cart';
import { baseApi } from '@/shared/api';
import { userReducer } from '@/entities/user';

export const store = configureStore({
  reducer: {
    cart: cartReducer,
    [baseApi.reducerPath]: baseApi.reducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(baseApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
