export type ProductColor = {
  id: string;
  name: string;
  value?: string;
  backgroundImage?: string;
};

export type Product = {
  id: string;
  categoryId?: string;
  title: string;
  image: string;
  price: string;
  oldPrice?: string;
  colors: ProductColor[];
  filterTags?: Record<string, string[]>;
  isSoldOut?: boolean;
};
