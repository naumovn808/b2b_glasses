import { baseApi } from '@/shared/api';
import type { AboutUs } from '../model/types';

export const aboutApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getAbout: build.query<AboutUs, void>({
      query: () => '/content/about/',
      providesTags: ['About'],
    }),
  }),
});

export const { useGetAboutQuery } = aboutApi;
