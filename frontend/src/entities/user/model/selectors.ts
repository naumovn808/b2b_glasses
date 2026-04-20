import type { RootState } from '@/app/providers/store/store';

export const selectUserToken = (state: RootState) => state.user.token;
export const selectUserIsLoading = (state: RootState) => state.user.isLoading;
export const selectUserError = (state: RootState) => state.user.error;
export const selectUserInited = (state: RootState) => state.user._inited;
export const selectUserIsAuth = (state: RootState) => !!state.user.token;
