import type {
  AddCartItemRequest,
  CheckoutCartResponse,
  CustomOrder,
  CustomOrderRequest,
  Order,
  OrderHistoryParams,
  OrderHistoryResponse,
  OrderItem,
  PartialUpdateCartItemRequest,
  UpdateCartItemRequest,
} from '../model/apiTypes';

import { baseApi } from '@/shared/api';

export const cartApi = baseApi.injectEndpoints({
  endpoints: (build) => ({
    getCart: build.query<Order, void>({
      query: () => '/orders/cart/',
      providesTags: ['Cart'],
    }),
    addCartItem: build.mutation<Order, AddCartItemRequest>({
      query: (body) => ({
        url: '/orders/cart/add/',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Cart'],
    }),
    checkoutCart: build.mutation<CheckoutCartResponse, void>({
      query: () => ({
        url: '/orders/cart/checkout/',
        method: 'POST',
      }),
      invalidatesTags: ['Cart', 'OrderHistory'],
    }),
    clearCart: build.mutation<void, void>({
      query: () => ({
        url: '/orders/cart/clear/',
        method: 'DELETE',
      }),
      invalidatesTags: ['Cart'],
    }),
    deleteCartItem: build.mutation<void, number>({
      query: (id) => ({
        url: `/orders/cart/items/${id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Cart'],
    }),
    updateCartItem: build.mutation<OrderItem, UpdateCartItemRequest>({
      query: ({ data, id }) => ({
        url: `/orders/cart/items/${id}/update/`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['Cart'],
    }),
    partialUpdateCartItem: build.mutation<
      OrderItem,
      PartialUpdateCartItemRequest
    >({
      query: ({ data, id }) => ({
        url: `/orders/cart/items/${id}/update/`,
        method: 'PATCH',
        body: data,
      }),
      async onQueryStarted({ data, id }, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          cartApi.util.updateQueryData('getCart', undefined, (draft) => {
            const item = draft.items.find((item) => item.id === id);
            if (item) {
              Object.assign(item, data);
            }
          }),
        );
        try {
          const { data: updatedItem } = await queryFulfilled;
          dispatch(
            cartApi.util.updateQueryData('getCart', undefined, (draft) => {
              const item = draft.items.find((item) => item.id === id);
              if (item) {
                Object.assign(item, updatedItem);
              }
            }),
          );
        } catch {
          patchResult.undo();
        }
      },
    }),
    createCustomOrder: build.mutation<CustomOrder, CustomOrderRequest>({
      query: (body) => ({
        url: '/orders/custom/create/',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['CustomOrders', 'OrderHistory'],
    }),
    getOrderHistory: build.query<
      OrderHistoryResponse,
      OrderHistoryParams | void
    >({
      query: (params) => ({
        url: '/orders/history/',
        params: params ?? undefined,
      }),
      providesTags: ['OrderHistory'],
    }),
  }),
});

export const {
  useAddCartItemMutation,
  useCheckoutCartMutation,
  useClearCartMutation,
  useCreateCustomOrderMutation,
  useDeleteCartItemMutation,
  useGetCartQuery,
  useGetOrderHistoryQuery,
  usePartialUpdateCartItemMutation,
  useUpdateCartItemMutation,
} = cartApi;
