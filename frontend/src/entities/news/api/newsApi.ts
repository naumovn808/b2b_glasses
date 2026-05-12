import { baseApi } from '@/shared/api';
import type { News, NewsParams, NewsResponse } from '../model/types';

export const newsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getNews: build.query<NewsResponse, NewsParams | void>({
      query: (params) => ({
        url: '/content/news/',
        params: params ?? undefined,
      }),
      providesTags: ['News'],
    }),
    getNewsById: build.query<News, number | string>({
      query: (id) => `/content/news/${id}/`,
      providesTags: (_result, _error, id) => [{ type: 'News', id }],
    }),
  }),
});

export const { useGetNewsByIdQuery, useGetNewsQuery } = newsApi;
