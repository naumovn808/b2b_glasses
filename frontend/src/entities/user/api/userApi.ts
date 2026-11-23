import { baseApi } from '@/shared/api';
import type { SetPasswordRequest, SetPasswordResponse, User } from '../model/types';

export const userApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getUserProfile: build.query<User, void>({
      query: () => '/auth/me/',
      providesTags: ['User'],
    }),
    setPassword: build.mutation<SetPasswordResponse, SetPasswordRequest>({
      query: (body) => ({
        url: '/auth/set-password/',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['User'],
    }),
  }),
});

export const { useGetUserProfileQuery, useSetPasswordMutation } = userApi;
