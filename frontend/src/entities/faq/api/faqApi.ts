import { baseApi } from '@/shared/api';
import type { FaqParams, FaqResponse } from '../model/types';

export const faqApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getFaq: build.query<FaqResponse, FaqParams | void>({
      query: (params) => ({
        url: '/content/faq/',
        params: params ?? undefined,
      }),
      providesTags: ['FAQ'],
    }),
  }),
});

export const { useGetFaqQuery } = faqApi;
