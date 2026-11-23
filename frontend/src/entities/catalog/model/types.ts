import type { PaginatedResponse, PaginationParams } from '@/shared/api';

export type ProductColor = {
  id: number;
  name?: string;
  hex_value: string;
  order?: number;
};

export type ProductImage = {
  id: number;
  image: string;
  order?: number;
};

export type Frame = {
  id: number;
  id_1c: string;
  name: string;
  sku: string;
  brand: string;
  material: string;
  shape: string;
  type: string;
  gender: string;
  age_group: string;
  size_a?: string | null;
  size_b?: string | null;
  size_d?: string | null;
  size_temple?: string | null;
  price: string;
  stock?: number;
  colors?: ProductColor[];
  images?: ProductImage[];
};

export type FramesParams = PaginationParams & {
  brand?: string;
  material?: string;
  shape?: string;
  type?: string;
  gender?: string;
  age_group?: string;
  colors?: string;
  price__gte?: number;
  price__lte?: number;
  search?: string;
};

export type FramesResponse = PaginatedResponse<Frame>;

export type FrameFilters = Record<string, unknown>;

export type Lens = {
  id: number;
  id_1c: string;
  name?: string;
  sku?: string;
  barcode?: string | null;
  series: string;
  sph: string;
  cyl: string;
  dia: number | null;
  price: string;
  stock?: number;
  colors?: ProductColor[];
  images?: ProductImage[];
};

export type LensesParams = PaginationParams & {
  series?: string;
  sph?: string;
  cyl?: string;
  dia?: string;
  search?: string;
};

export type LensesResponse = PaginatedResponse<Lens>;

export type LensOptions = Record<string, unknown>;

export type CatalogProductType = 'frame' | 'lens';

export type CatalogProductDetail =
  | {
      type: 'frame';
      item: Frame;
    }
  | {
      type: 'lens';
      item: Lens;
    };

export type CatalogProductDetailParams = {
  id: number | string;
  type: CatalogProductType;
};
