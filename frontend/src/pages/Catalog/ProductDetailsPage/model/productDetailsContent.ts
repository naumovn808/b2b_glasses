import Photo2 from '@/shared/assets/image/news/news-2.png';
import type { Product } from '@/entities/product';

type ProductDetailsOption = {
  id: string;
  label: string;
};

export type ProductDetailsOptionGroup = {
  id: string;
  title: string;
  options: ProductDetailsOption[];
  selectedOptionId: string;
};

export type ProductDetails = Product & {
  categoryKey: string;
  discountPercent: number;
  frameNoticeKey: string;
  gallery: string[];
  rating: number;
  reviewCount: number;
  sizes: string[];
  selectedSize: string;
  stockTextKey: string;
  viewersTextKey: string;
  optionGroups?: ProductDetailsOptionGroup[];
};

type ProductDetailPreset = {
  categoryKey: string;
  frameNoticeKey: string;
  optionGroups?: ProductDetailsOptionGroup[];
  sizes: string[];
  selectedSize: string;
  stockTextKey: string;
  viewersTextKey: string;
};

const DEFAULT_DETAIL_PRESET: ProductDetailPreset = {
  categoryKey: 'productDetail.category.default',
  frameNoticeKey: 'productDetail.frameNotice.onlyFourLeft',
  sizes: ['M', 'XL', 'XXL'],
  selectedSize: 'M',
  stockTextKey: 'productDetail.stockText.discountPeriod',
  viewersTextKey: 'productDetail.viewers.productNow',
};

const DETAIL_PRESETS_BY_CATEGORY: Record<string, ProductDetailPreset> = {
  frames: {
    categoryKey: 'catalog.category.frames',
    frameNoticeKey: 'productDetail.frameNotice.onlyFourLeft',
    sizes: ['M', 'XL', 'XXL'],
    selectedSize: 'M',
    stockTextKey: 'productDetail.stockText.discountPeriod',
    viewersTextKey: 'productDetail.viewers.productNow',
  },
  lenses: {
    categoryKey: 'catalog.category.lenses',
    frameNoticeKey: 'productDetail.frameNotice.onlyFourLeft',
    optionGroups: [
      {
        id: 'design',
        title: 'Дизайн',
        selectedOptionId: 'single-vision-sp',
        options: [
          { id: 'single-vision-sp', label: 'Однофокальные SP' },
          { id: 'single-vision-as', label: 'Однофокальные AS' },
          { id: 'single-vision-das', label: 'Однофокальные DAS' },
          { id: 'office', label: 'Офисные' },
          { id: 'relax', label: 'Разгрузочные' },
          { id: 'myopia-control', label: 'Контроль Миопии' },
        ],
      },
      {
        id: 'index',
        title: 'Индекс',
        selectedOptionId: '1.50',
        options: [
          { id: '1.50', label: '1.50' },
          { id: '1.56', label: '1.56' },
          { id: '1.59', label: '1.59' },
          { id: '1.60', label: '1.60' },
          { id: '1.67', label: '1.67' },
          { id: '1.74', label: '1.74' },
        ],
      },
      {
        id: 'material',
        title: 'Материал',
        selectedOptionId: 'transparent',
        options: [
          { id: 'transparent', label: 'Прозрачные' },
          { id: 'tinted', label: 'Окрашенные' },
          { id: 'bct-ng', label: 'BCT NG' },
          { id: 'transitions-gen-s', label: 'Transitions Gen S' },
          { id: 'transitions-xtx-ng', label: 'Transitions XTX NG' },
          { id: 'neochrome', label: 'NeoChrome' },
          { id: 'chrome', label: 'Chrome' },
        ],
      },
      {
        id: 'coating',
        title: 'Покрытия',
        selectedOptionId: 'none',
        options: [
          { id: 'none', label: 'Без покрытия' },
          { id: 'protect-ar-plus', label: 'ProtectAR+' },
          { id: 'protect-ar-blue', label: 'ProtectAR+Blue' },
          { id: 'protect-ar-drive', label: 'ProtectAR+Drive' },
        ],
      },
    ],
    sizes: ['1.50', '1.56', '1.60', '1.67', '1.74'],
    selectedSize: '1.56',
    stockTextKey: 'productDetail.stockText.discountPeriod',
    viewersTextKey: 'productDetail.viewers.productNow',
  },
  contacts: {
    categoryKey: 'catalog.category.contacts',
    frameNoticeKey: 'productDetail.frameNotice.onlyFourLeft',
    optionGroups: [
      {
        id: 'replacement-period',
        title: 'Срок замены',
        selectedOptionId: '1-day',
        options: [
          { id: '1-day', label: 'Один день' },
          { id: '2-weeks', label: '2 недели' },
          { id: '1-month', label: '1 месяц' },
          { id: '3-months', label: '3 месяца' },
          { id: '6-months', label: '6 месяцев' },
        ],
      },
      {
        id: 'radius',
        title: 'Радиус',
        selectedOptionId: '8.4',
        options: [
          { id: '8.4', label: '8.4' },
          { id: '8.5', label: '8.5' },
        ],
      },
      {
        id: 'material',
        title: 'Материал',
        selectedOptionId: 'hydrogel',
        options: [
          { id: 'hydrogel', label: 'Гидрогель' },
          { id: 'silicone-hydrogel', label: 'Селиконгидрогель' },
        ],
      },
    ],
    sizes: ['8.4', '8.5', '8.6'],
    selectedSize: '8.4',
    stockTextKey: 'productDetail.stockText.discountPeriod',
    viewersTextKey: 'productDetail.viewers.productNow',
  },
  accessories: {
    categoryKey: 'catalog.category.accessories',
    frameNoticeKey: 'productDetail.frameNotice.onlyFourLeft',
    sizes: ['S', 'M', 'L', 'XL'],
    selectedSize: 'M',
    stockTextKey: 'productDetail.stockText.discountPeriod',
    viewersTextKey: 'productDetail.viewers.accessoryNow',
  },
};

function getPriceValue(price: string) {
  const normalizedPrice = price.replace(',', '.').replace(/[^\d.]/g, '');

  return Number(normalizedPrice) || 0;
}

function getDiscountPercent(price: string, oldPrice?: string) {
  if (!oldPrice) return 0;

  const currentPrice = getPriceValue(price);
  const previousPrice = getPriceValue(oldPrice);

  if (previousPrice <= 0) return 0;

  return Math.round(((previousPrice - currentPrice) / previousPrice) * 100);
}

export function createProductDetails(product: Product): ProductDetails {
  const preset =
    DETAIL_PRESETS_BY_CATEGORY[product.categoryId ?? ''] ??
    DEFAULT_DETAIL_PRESET;
  const discountPercent = getDiscountPercent(product.price, product.oldPrice);

  return {
    ...product,
    categoryKey: preset.categoryKey,
    discountPercent,
    frameNoticeKey: preset.frameNoticeKey,
    gallery: [product.image, Photo2],
    rating: 3,
    reviewCount: 3,
    sizes: preset.sizes,
    selectedSize: preset.selectedSize,
    stockTextKey: preset.stockTextKey,
    viewersTextKey: preset.viewersTextKey,
    optionGroups: preset.optionGroups,
  };
}
