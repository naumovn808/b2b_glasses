import type {
  Frame,
  FramesParams,
  Lens,
  LensesParams,
} from '@/entities/catalog';

import type { CatalogFilterGroup } from './catalogContent';
import NoPhoto from '@/shared/assets/image/catalog/no-photo.png';
import type { ProductCardProduct } from '@/features/product-card';

export const PRODUCTS_PER_PAGE = 6;

export type CatalogCategoryId = 'frames' | 'lenses';
export type CatalogSearchFilters = Record<string, string[]>;

const reservedSearchParams = new Set(['category', 'page', 'sort']);

const frameFilterConfigs: Array<{
  id: string;
  apiKeys: string[];
  title: string;
  variant: CatalogFilterGroup['variant'];
}> = [
  {
    id: 'age_group',
    apiKeys: ['age_group', 'age_groups'],
    title: 'Возрастные группы',
    variant: 'inline',
  },
  {
    id: 'gender',
    apiKeys: ['gender', 'genders'],
    title: 'Пол',
    variant: 'inline',
  },
  {
    id: 'brand',
    apiKeys: ['brand', 'brands'],
    title: 'Бренд',
    variant: 'inline',
  },
  {
    id: 'shape',
    apiKeys: ['shape', 'shapes'],
    title: 'Форма',
    variant: 'stack',
  },
  {
    id: 'material',
    apiKeys: ['material', 'materials'],
    title: 'Материал',
    variant: 'stack',
  },
  { id: 'type', apiKeys: ['type', 'types'], title: 'Тип', variant: 'stack' },
  {
    id: 'colors',
    apiKeys: ['colors'],
    title: 'Цвет',
    variant: 'colors',
  },
];

const lensFilterConfigs: Array<{
  id: string;
  apiKeys: string[];
  title: string;
  variant: CatalogFilterGroup['variant'];
}> = [
  { id: 'series', apiKeys: ['series'], title: 'Серия', variant: 'stack' },
  { id: 'sph', apiKeys: ['sph'], title: 'SPH', variant: 'stack' },
  { id: 'cyl', apiKeys: ['cyl'], title: 'CYL', variant: 'stack' },
  { id: 'dia', apiKeys: ['dia'], title: 'DIA', variant: 'stack' },
];

function getPriceValue(price: string) {
  const normalizedPrice = price.replace(',', '.').replace(/[^\d.]/g, '');

  return Number(normalizedPrice) || 0;
}

function getDiscountValue(price: string, oldPrice?: string) {
  if (!oldPrice) return 0;

  const currentPrice = getPriceValue(price);
  const previousPrice = getPriceValue(oldPrice);

  if (previousPrice <= 0) return 0;

  return Math.round(((previousPrice - currentPrice) / previousPrice) * 100);
}

function getFirstSelectedFilter(
  activeFilters: CatalogSearchFilters,
  filterId: string,
) {
  return activeFilters[filterId]?.join(',');
}

function getProductImage(
  apiImages: Array<{ image: string }> | undefined,
  fallbackImage: string,
) {
  return apiImages?.[0]?.image ?? fallbackImage;
}

function getProductImages(
  apiImages: Array<{ image: string }> | undefined,
  fallbackImage: string,
) {
  if (!apiImages || apiImages.length === 0) {
    return [fallbackImage];
  }

  return apiImages.map((image) => image.image);
}

function getProductColors(
  apiColors:
    | Array<{ hex_value: string; id: number; name?: string }>
    | undefined,
  fallback: { id: string; name: string; value: string },
) {
  if (!apiColors || apiColors.length === 0) {
    return [fallback];
  }

  return apiColors.map((color) => ({
    id: String(color.id),
    name: color.name || color.hex_value,
    value: color.hex_value,
  }));
}

function normalizeFilterOption(rawOption: unknown) {
  if (rawOption && typeof rawOption === 'object' && !Array.isArray(rawOption)) {
    const option = rawOption as Record<string, unknown>;
    const id =
      option.id ?? option.value ?? option.slug ?? option.key ?? option.name;
    const label = option.name ?? option.label ?? option.title ?? id;

    if (id !== undefined && label !== undefined) {
      return {
        id: String(id),
        label: String(label),
        value: option.hex_value ? String(option.hex_value) : undefined,
      };
    }
  }

  if (typeof rawOption === 'string' || typeof rawOption === 'number') {
    return {
      id: String(rawOption),
      label: String(rawOption),
    };
  }

  return null;
}

function normalizeFilterOptions(rawOptions: unknown) {
  if (Array.isArray(rawOptions)) {
    return rawOptions.map(normalizeFilterOption).filter((option) => !!option);
  }

  if (
    rawOptions &&
    typeof rawOptions === 'object' &&
    !Array.isArray(rawOptions)
  ) {
    return Object.entries(rawOptions).map(([id, label]) => ({
      id,
      label: String(label),
    }));
  }

  return [];
}

function getApiFilterValue(
  apiFilters: Record<string, unknown> | undefined,
  keys: string[],
) {
  return keys.map((key) => apiFilters?.[key]).find((value) => value);
}

export function getCatalogCategory(searchParams: URLSearchParams) {
  return searchParams.get('category') === 'lenses' ? 'lenses' : 'frames';
}

export function getCatalogPage(searchParams: URLSearchParams) {
  const page = Number(searchParams.get('page'));

  return Number.isInteger(page) && page > 0 ? page : 1;
}

export function getCatalogSort(
  searchParams: URLSearchParams,
  defaultSortId: string,
) {
  return searchParams.get('sort') ?? defaultSortId;
}

export function getCatalogFilters(searchParams: URLSearchParams) {
  const filters: CatalogSearchFilters = {};

  searchParams.forEach((value, key) => {
    if (reservedSearchParams.has(key) || !value) {
      return;
    }

    filters[key] = value.split(',').filter(Boolean);
  });

  return filters;
}

export function hasCatalogFilters(activeFilters: CatalogSearchFilters) {
  return Object.values(activeFilters).some((filters) => filters.length > 0);
}

export function getCatalogFilterGroups(
  category: CatalogCategoryId,
  apiFilters: Record<string, unknown> | undefined,
) {
  const configs =
    category === 'frames' ? frameFilterConfigs : lensFilterConfigs;

  return configs
    .map((config) => {
      const options = normalizeFilterOptions(
        getApiFilterValue(apiFilters, config.apiKeys),
      );

      if (options.length === 0) {
        return null;
      }

      return {
        id: config.id,
        title: config.title,
        variant: config.variant,
        isCollapsible: true,
        options,
      } as CatalogFilterGroup;
    })
    .filter((group) => !!group);
}

export function createFramesParams(
  activeFilters: CatalogSearchFilters,
  page: number,
): FramesParams {
  return {
    age_group: getFirstSelectedFilter(activeFilters, 'age_group'),
    brand: getFirstSelectedFilter(activeFilters, 'brand'),
    gender: getFirstSelectedFilter(activeFilters, 'gender'),
    material: getFirstSelectedFilter(activeFilters, 'material'),
    page,
    page_size: PRODUCTS_PER_PAGE,
    shape: getFirstSelectedFilter(activeFilters, 'shape'),
    type: getFirstSelectedFilter(activeFilters, 'type'),
    colors: getFirstSelectedFilter(activeFilters, 'colors'),
  };
}

export function createLensesParams(
  activeFilters: CatalogSearchFilters,
  page: number,
): LensesParams {
  return {
    cyl: getFirstSelectedFilter(activeFilters, 'cyl'),
    dia: getFirstSelectedFilter(activeFilters, 'dia'),
    page,
    page_size: PRODUCTS_PER_PAGE,
    series: getFirstSelectedFilter(activeFilters, 'series'),
    sph: getFirstSelectedFilter(activeFilters, 'sph'),
  };
}

function formatCatalogPrice(price: string) {
  return `$${price}`;
}

export function mapFrameToProduct(frame: Frame): ProductCardProduct {
  const sizes = [
    frame.size_a,
    frame.size_b,
    frame.size_d,
    frame.size_temple,
  ].filter((size): size is string => Boolean(size));

  return {
    id: `frame-${frame.id}`,
    apiProductId: frame.id,
    apiProductType: 'frame',
    categoryId: 'frames',
    title: frame.name,
    image: getProductImage(frame.images, NoPhoto),
    images: getProductImages(frame.images, NoPhoto),
    price: formatCatalogPrice(frame.price),
    colors: getProductColors(frame.colors, {
      id: 'default',
      name: 'Цвет',
      value: '#d8d8d8',
    }),
    sizes,
    isSoldOut: frame.stock === 0,
    stock: frame.stock,
  };
}

export function mapLensToProduct(lens: Lens): ProductCardProduct {
  return {
    id: `lens-${lens.id}`,
    apiProductId: lens.id,
    apiProductType: 'lens',
    categoryId: 'lenses',
    title: lens.name || lens.series,
    image: getProductImage(lens.images, NoPhoto),
    images: getProductImages(lens.images, NoPhoto),
    price: formatCatalogPrice(lens.price),
    colors: [],
    sizes: [],
    isSoldOut: lens.stock === 0,
    stock: lens.stock,
  };
}

export function sortCatalogProducts(
  products: ProductCardProduct[],
  sortId: string,
) {
  return [...products].sort((firstProduct, secondProduct) => {
    if (sortId === 'cheap-first') {
      return (
        getPriceValue(firstProduct.price) - getPriceValue(secondProduct.price)
      );
    }

    if (sortId === 'expensive-first') {
      return (
        getPriceValue(secondProduct.price) - getPriceValue(firstProduct.price)
      );
    }

    if (sortId === 'discount-first') {
      return (
        getDiscountValue(secondProduct.price, secondProduct.oldPrice) -
        getDiscountValue(firstProduct.price, firstProduct.oldPrice)
      );
    }

    return 0;
  });
}

export function updateCatalogSearchParams(
  searchParams: URLSearchParams,
  update: (params: URLSearchParams) => void,
) {
  const nextParams = new URLSearchParams(searchParams);
  update(nextParams);
  return nextParams;
}

export function clearCatalogFilterParams(searchParams: URLSearchParams) {
  const filterKeys: string[] = [];

  searchParams.forEach((_, key) => {
    if (!reservedSearchParams.has(key)) {
      filterKeys.push(key);
    }
  });

  filterKeys.forEach((key) => searchParams.delete(key));
}
