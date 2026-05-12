import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import type { RootState } from '@/app/providers/store/store';

export const API_BASE_URL = '/api/v1';

export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const state = getState() as RootState;
      const token = state.user.token;
      if (token) {
        headers.set('authorization', `Token ${token}`);
      }

      headers.set('Content-Type', 'application/json');

      return headers;
    },
  }),

  tagTypes: [
    'About',
    'Contacts',
    'FAQ',
    'Frames',
    'FrameFilters',
    'Lenses',
    'LensOptions',
    'News',
    'Cart',
    'OrderHistory',
    'CustomOrders',
    'Training',
  ],
  endpoints: () => ({}),
});
