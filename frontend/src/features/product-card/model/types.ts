export type ProductCardColor = {
  id: string;
  name: string;
  value?: string;
  backgroundImage?: string;
};

export type ProductCardProduct = {
  id: string;
  apiProductId?: number;
  apiProductType?: 'frame' | 'lens';
  categoryId?: string;
  sizes: string[];
  title: string;
  image: string;
  images?: string[];
  price: string;
  oldPrice?: string;
  colors: ProductCardColor[];
  filterTags?: Record<string, string[]>;
  isSoldOut?: boolean;
  stock?: number;
};
