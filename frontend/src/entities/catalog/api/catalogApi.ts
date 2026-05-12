import { baseApi } from '@/shared/api';
import type {
  CatalogProductDetail,
  CatalogProductDetailParams,
  FrameFilters,
  FramesParams,
  FramesResponse,
  LensOptions,
  LensesParams,
  LensesResponse,
} from '../model/types';

export const catalogApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getFrames: build.query<FramesResponse, FramesParams | void>({
      query: (params) => ({
        url: '/catalog/frames/',
        params: params ?? undefined,
      }),
      providesTags: ['Frames'],
    }),
    getFrameFilters: build.query<FrameFilters, void>({
      query: () => '/catalog/frames/filters/',
      providesTags: ['FrameFilters'],
    }),
    getLenses: build.query<LensesResponse, LensesParams | void>({
      query: (params) => ({
        url: '/catalog/lenses/',
        params: params ?? undefined,
      }),
      providesTags: ['Lenses'],
    }),
    getLensOptions: build.query<LensOptions, void>({
      query: () => '/catalog/lenses/options/',
      providesTags: ['LensOptions'],
    }),
    getProductById: build.query<
      CatalogProductDetail,
      CatalogProductDetailParams
    >({
      query: ({ id, type }) => `/catalog/products/${type}/${id}/`,
      providesTags: (_result, _error, { id, type }) => [
        { type: type === 'frame' ? 'Frames' : 'Lenses', id },
      ],
    }),
  }),
});

export const {
  useGetFrameFiltersQuery,
  useGetFramesQuery,
  useGetLensOptionsQuery,
  useGetLensesQuery,
  useGetProductByIdQuery,
} = catalogApi;
