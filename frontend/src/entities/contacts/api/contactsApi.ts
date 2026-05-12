import { baseApi } from '@/shared/api';
import type { Contacts } from '../model/types';

export const contactsApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getContacts: build.query<Contacts, void>({
      query: () => '/content/contacts/',
      providesTags: ['Contacts'],
    }),
  }),
});

export const { useGetContactsQuery } = contactsApi;
