export type CartItem = {
  id: string;
  productId: string;
  title: string;
  image: string;
  price: string;
  oldPrice?: string;
  color: string;
  colorId?: string;
  size: string;
  stockText: string;
  quantity: number;
};

export type AddCartItemPayload = Omit<CartItem, 'id'>;
