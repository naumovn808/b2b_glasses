import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { User, UserSchema } from './types';

const AUTH_TOKEN_KEY = 'authToken';

const initialState: UserSchema = {
  _inited: false,
  isLoading: false,
  isAuthModalOpen: false,
};

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setAuthData: (state, action: PayloadAction<User>) => {
      state.authData = action.payload;
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      localStorage.setItem(AUTH_TOKEN_KEY, action.payload);
    },
    initAuthData: (state) => {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      if (token) {
        state.token = token;
      }
      state._inited = true;
    },
    logout: (state) => {
      state.authData = undefined;
      state.token = undefined;
      localStorage.removeItem(AUTH_TOKEN_KEY);
    },
    setError: (state, action: PayloadAction<string | undefined>) => {
      state.error = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    openAuthModal: (state) => {
      state.isAuthModalOpen = true;
    },
    closeAuthModal: (state) => {
      state.isAuthModalOpen = false;
      state.error = undefined;
    },
  },
});

export const { actions: userActions } = userSlice;
export const { reducer: userReducer } = userSlice;
