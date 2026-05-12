import type { PaginatedResponse, PaginationParams } from '@/shared/api';

export type ProductType = 'frame' | 'lens';

export type OrderStatus = 'cart' | 'pending' | 'completed' | 'cancelled';

export type CustomOrderStatus =
  | 'new'
  | 'processing'
  | 'completed'
  | 'cancelled';

export type OrderItem = {
  id: number;
  product: string;
  stock: number;
  image: string;
  quantity?: number;
  price_at_order: string;
  total_price: string;
};

export type Order = {
  id: number;
  user: number;
  status?: OrderStatus;
  total_price?: string;
  created_at: string;
  items: OrderItem[];
};

export type AddCartItemRequest = {
  product_type: ProductType;
  product_id: number;
  quantity?: number;
};

export type UpdateCartItemRequest = {
  id: number;
  data: {
    quantity?: number;
    price_at_order: string;
  };
};

export type PartialUpdateCartItemRequest = {
  id: number;
  data: Partial<Pick<OrderItem, 'quantity' | 'price_at_order'>>;
};

export type CheckoutCartResponse = {
  detail?: string;
};

export type CustomOrderRequest = {
  series: string;
  sph: string;
  cyl: string;
  dia?: string | null;
  design: string;
  photochrom: string;
};

export type CustomOrder = CustomOrderRequest & {
  id: number;
  status?: CustomOrderStatus;
  created_at: string;
};

export type OrderHistoryParams = PaginationParams;

export type OrderHistoryResponse = PaginatedResponse<Order>;
