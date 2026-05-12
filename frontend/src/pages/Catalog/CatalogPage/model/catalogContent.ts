import Accessories from '@/shared/assets/image/catalog/accessories.png';
import ContactLenses from '@/shared/assets/image/catalog/contact-lenses.png';
import Frames from '@/shared/assets/image/catalog/frames.png';
import Lenses from '@/shared/assets/image/catalog/lenses.png';

export const catalogCategories = [
  {
    id: 'frames',
    title: 'Оправы',
    image: Frames,
  },
  {
    id: 'lenses',
    title: 'Линзы',
    image: Lenses,
  },
  {
    id: 'contacts',
    title: 'Контактные линзы',
    image: ContactLenses,
    disabled: true,
  },
  {
    id: 'accessories',
    title: 'Аксессуары',
    image: Accessories,
    disabled: true,
  },
];

export const catalogSortOptions = [
  { id: 'cheap-first', label: 'Сначала недорогие' },
  { id: 'expensive-first', label: 'Сначала дорогие' },
  { id: 'popular-first', label: 'Сначала популярные' },
  { id: 'new-first', label: 'По новинкам' },
  { id: 'discount-first', label: 'По скидке (%)' },
];

type CatalogFilterOption = {
  id: string;
  label: string;
};

export type CatalogFilterGroup =
  | {
      id: string;
      title: string;
      variant: 'inline' | 'stack' | 'size';
      options: CatalogFilterOption[];
      isCollapsible?: boolean;
    }
  | {
      id: string;
      title: string;
      variant: 'colors';
      options: Array<CatalogFilterOption & { value: string }>;
    };
