import { baseApi } from '@/shared/api';
import type { Training, TrainingParams, TrainingResponse } from '../model/types';

export const trainingApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getTraining: build.query<TrainingResponse, TrainingParams | void>({
      query: (params) => ({
        url: '/content/training/',
        params: params ?? undefined,
      }),
      providesTags: ['Training'],
    }),
    getTrainingById: build.query<Training, number | string>({
      query: (id) => `/content/training/${id}/`,
      providesTags: (_result, _error, id) => [{ type: 'Training', id }],
    }),
  }),
});

export const { useGetTrainingByIdQuery, useGetTrainingQuery } = trainingApi;
