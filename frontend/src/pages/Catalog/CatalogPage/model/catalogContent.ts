import Accessories from '@/shared/assets/image/catalog/accessories.png';
import ContactLenses from '@/shared/assets/image/catalog/contact-lenses.png';
import Frames from '@/shared/assets/image/catalog/frames.png';
import Lenses from '@/shared/assets/image/catalog/lenses.png';
import type { Product } from '@/entities/product';
import edu1 from '@/shared/assets/image/edu/edu-1.png';
import news1 from '@/shared/assets/image/news/news-1.png';
import news2 from '@/shared/assets/image/news/news-2.png';
import news3 from '@/shared/assets/image/news/news-3.png';
import news4 from '@/shared/assets/image/news/news-4.png';
import newsMob from '@/shared/assets/image/news-mob.png';

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
  },
  {
    id: 'accessories',
    title: 'Аксессуары',
    image: Accessories,
  },
];

export const catalogSortOptions = [
  { id: 'cheap-first', label: 'Сначала недорогие' },
  { id: 'expensive-first', label: 'Сначала дорогие' },
  { id: 'popular-first', label: 'Сначала популярные' },
  { id: 'new-first', label: 'По новинкам' },
  { id: 'discount-first', label: 'По скидке (%)' },
];

export const catalogProducts: Product[] = [
  {
    id: 'briony-red',
    categoryId: 'frames',
    title: 'Briony',
    image: news1,
    price: '3000.00Р',
    filterTags: {
      age: ['adult'],
      gender: ['unisex', 'male'],
      color: ['yellow'],
      price: ['2000-5000'],
      brand: ['minimo'],
      shape: ['square'],
      material: ['acetate'],
    },
    colors: [
      { id: 'yellow', name: 'Желтый', value: '#ffd51f' },
      { id: 'black', name: 'Черный', value: '#000000' },
    ],
  },
  {
    id: 'briony-blue',
    categoryId: 'frames',
    title: 'Briony',
    image: news2,
    price: '3000.00Р',
    isSoldOut: true,
    filterTags: {
      age: ['teen'],
      gender: ['female', 'unisex'],
      color: ['blue', 'pink'],
      price: ['2000-5000'],
      brand: ['retrio-brook'],
      shape: ['round'],
      material: ['metal'],
    },
    colors: [
      { id: 'blue', name: 'Голубой', value: '#9fcae1' },
      { id: 'pink', name: 'Розовый', value: '#ffc8d2' },
    ],
  },
  {
    id: 'briony-violet',
    categoryId: 'contacts',
    title: 'Briony',
    image: news3,
    price: '3000.00Р',
    filterTags: {
      color: ['green'],
      price: ['2000-5000'],
      'wearing-mode': ['daily'],
    },
    colors: [
      { id: 'white', name: 'Белый', value: '#ffffff' },
      { id: 'green', name: 'Зеленый', value: '#c7e3ca' },
    ],
  },
  {
    id: 'briony-red-frame',
    categoryId: 'lenses',
    title: 'Briony',
    image: newsMob,
    price: '3000.00Р',
    filterTags: {
      color: ['blue'],
      price: ['2000-5000'],
      type: ['single-vision'],
      coating: ['anti-reflective'],
    },
    colors: [
      { id: 'light-blue', name: 'Светло-голубой', value: '#cce8f3' },
      { id: 'deep-blue', name: 'Темно-синий', value: '#0a4f70' },
    ],
  },
  {
    id: 'briony-clear',
    categoryId: 'accessories',
    title: 'Briony',
    image: edu1,
    price: '3000.00Р',
    filterTags: {
      color: ['mint'],
      price: ['2000-5000'],
      category: ['cases'],
    },
    colors: [
      { id: 'mint', name: 'Мятный', value: '#d4efd8' },
      {
        id: 'pattern',
        name: 'Черепаховый',
        backgroundImage:
          'linear-gradient(45deg, #ffffff 0 25%, #111111 25% 35%, #ffffff 35% 50%, #111111 50% 60%, #ffffff 60% 100%)',
      },
    ],
  },
  {
    id: 'briony-gold',
    categoryId: 'frames',
    title: 'Briony',
    image: news4,
    price: '3000.00Р',
    oldPrice: '5000.00Р',
    filterTags: {
      age: ['adult'],
      gender: ['female'],
      color: ['pink'],
      price: ['2000-5000'],
      brand: ['learts'],
      shape: ['oval'],
      material: ['combined'],
    },
    colors: [
      { id: 'rose', name: 'Розовый', value: '#ffc8d2' },
      { id: 'lilac', name: 'Лиловый', value: '#cdb4cf' },
      { id: 'white', name: 'Белый', value: '#ffffff' },
    ],
  },
  {
    id: 'retrio-sky',
    categoryId: 'frames',
    title: 'Retrio Sky',
    image: news1,
    price: '1800.00Р',
    filterTags: {
      age: ['child'],
      gender: ['unisex'],
      color: ['blue'],
      price: ['1000-2000'],
      brand: ['retrio-brook'],
      shape: ['round'],
      material: ['acetate'],
    },
    colors: [
      { id: 'sky', name: 'Небесный', value: '#85c7f2' },
      { id: 'white', name: 'Белый', value: '#ffffff' },
    ],
  },
  {
    id: 'learts-coral',
    categoryId: 'frames',
    title: 'Learts Coral',
    image: news2,
    price: '5200.00Р',
    oldPrice: '6800.00Р',
    filterTags: {
      age: ['adult'],
      gender: ['female'],
      color: ['coral', 'pink'],
      price: ['5000-10000'],
      brand: ['learts'],
      shape: ['round'],
      material: ['metal'],
    },
    colors: [
      { id: 'coral', name: 'Коралловый', value: '#ff6969' },
      { id: 'pink', name: 'Розовый', value: '#f481df' },
    ],
  },
  {
    id: 'vagabond-indigo',
    categoryId: 'frames',
    title: 'Vagabond Indigo',
    image: news3,
    price: '7400.00Р',
    filterTags: {
      age: ['adult'],
      gender: ['male'],
      color: ['indigo'],
      price: ['5000-10000'],
      brand: ['vagabond'],
      shape: ['square'],
      material: ['combined'],
    },
    colors: [
      { id: 'indigo', name: 'Индиго', value: '#6a79f0' },
      { id: 'black', name: 'Черный', value: '#000000' },
    ],
  },
  {
    id: 'abby-mint',
    categoryId: 'frames',
    title: 'Abby Mint',
    image: news4,
    price: '12500.00Р',
    oldPrice: '15000.00Р',
    filterTags: {
      age: ['teen'],
      gender: ['female'],
      color: ['mint'],
      price: ['10000-20000'],
      brand: ['abby'],
      shape: ['oval'],
      material: ['acetate'],
    },
    colors: [
      { id: 'mint', name: 'Мятный', value: '#78f0c7' },
      { id: 'violet', name: 'Фиолетовый', value: '#7e5ee7' },
    ],
  },
  {
    id: 'minimo-aqua',
    categoryId: 'frames',
    title: 'Minimo Aqua',
    image: edu1,
    price: '960.00Р',
    filterTags: {
      age: ['child'],
      gender: ['unisex'],
      color: ['aqua'],
      price: ['0-1000'],
      brand: ['minimo'],
      shape: ['oval'],
      material: ['metal'],
    },
    colors: [
      { id: 'aqua', name: 'Аква', value: '#77ecd9' },
      { id: 'yellow', name: 'Жёлтый', value: '#ffd84a' },
    ],
  },
  {
    id: 'lens-office-blue',
    categoryId: 'lenses',
    title: 'Office Blue',
    image: Lenses,
    price: '6200.00Р',
    filterTags: {
      color: ['blue'],
      price: ['5000-10000'],
      type: ['office'],
      coating: ['blue-light'],
    },
    colors: [
      { id: 'blue', name: 'Синий', value: '#82b3ee' },
      { id: 'cyan', name: 'Голубой', value: '#5fd6ef' },
    ],
  },
  {
    id: 'lens-progressive-photo',
    categoryId: 'lenses',
    title: 'Progressive Photo',
    image: news1,
    price: '11800.00Р',
    filterTags: {
      color: ['violet'],
      price: ['10000-20000'],
      type: ['progressive'],
      coating: ['photochromic'],
    },
    colors: [
      { id: 'violet', name: 'Фиолетовый', value: '#7e5ee7' },
      { id: 'purple', name: 'Пурпурный', value: '#ac72ed' },
    ],
  },
  {
    id: 'contacts-daily-cyan',
    categoryId: 'contacts',
    title: 'Daily Cyan',
    image: ContactLenses,
    price: '1400.00Р',
    filterTags: {
      color: ['cyan'],
      price: ['1000-2000'],
      'wearing-mode': ['daily'],
    },
    colors: [
      { id: 'cyan', name: 'Голубой', value: '#5fd6ef' },
      { id: 'sky', name: 'Небесный', value: '#85c7f2' },
    ],
  },
  {
    id: 'contacts-monthly-indigo',
    categoryId: 'contacts',
    title: 'Monthly Indigo',
    image: newsMob,
    price: '2800.00Р',
    filterTags: {
      color: ['indigo'],
      price: ['2000-5000'],
      'wearing-mode': ['monthly'],
    },
    colors: [
      { id: 'indigo', name: 'Индиго', value: '#6a79f0' },
      { id: 'blue', name: 'Синий', value: '#82b3ee' },
    ],
  },
  {
    id: 'contacts-extended-pink',
    categoryId: 'contacts',
    title: 'Extended Pink',
    image: news2,
    price: '5400.00Р',
    filterTags: {
      color: ['pink'],
      price: ['5000-10000'],
      'wearing-mode': ['extended'],
    },
    colors: [
      { id: 'pink', name: 'Розовый', value: '#f481df' },
      { id: 'coral', name: 'Коралловый', value: '#ff6969' },
    ],
  },
  {
    id: 'case-purple',
    categoryId: 'accessories',
    title: 'Case Purple',
    image: Accessories,
    price: '900.00Р',
    filterTags: {
      color: ['purple'],
      price: ['0-1000'],
      category: ['cases'],
    },
    colors: [
      { id: 'purple', name: 'Пурпурный', value: '#ac72ed' },
      { id: 'white', name: 'Белый', value: '#ffffff' },
    ],
  },
  {
    id: 'cloth-yellow',
    categoryId: 'accessories',
    title: 'Cloth Yellow',
    image: news3,
    price: '650.00Р',
    filterTags: {
      color: ['yellow'],
      price: ['0-1000'],
      category: ['cloths'],
    },
    colors: [
      { id: 'yellow', name: 'Жёлтый', value: '#ffd84a' },
      { id: 'mint', name: 'Мятный', value: '#78f0c7' },
    ],
  },
  {
    id: 'solution-aqua',
    categoryId: 'accessories',
    title: 'Solution Aqua',
    image: news4,
    price: '1600.00Р',
    filterTags: {
      color: ['aqua'],
      price: ['1000-2000'],
      category: ['solutions'],
    },
    colors: [
      { id: 'aqua', name: 'Аква', value: '#77ecd9' },
      { id: 'turquoise', name: 'Бирюзовый', value: '#68dce8' },
    ],
  },
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

const baseCatalogFilterGroups: CatalogFilterGroup[] = [
  {
    id: 'color',
    title: 'Цвет',
    variant: 'colors',
    options: [
      { id: 'red', label: 'Красный', value: '#ff6b5f' },
      { id: 'cyan', label: 'Голубой', value: '#5fd6ef' },
      { id: 'yellow', label: 'Жёлтый', value: '#ffd84a' },
      { id: 'green', label: 'Зелёный', value: '#82ee64' },
      { id: 'mint', label: 'Мятный', value: '#78f0c7' },
      { id: 'aqua', label: 'Аква', value: '#77ecd9' },
      { id: 'sky', label: 'Небесный', value: '#85c7f2' },
      { id: 'turquoise', label: 'Бирюзовый', value: '#68dce8' },
      { id: 'blue', label: 'Синий', value: '#82b3ee' },
      { id: 'indigo', label: 'Индиго', value: '#6a79f0' },
      { id: 'violet', label: 'Фиолетовый', value: '#7e5ee7' },
      { id: 'purple', label: 'Пурпурный', value: '#ac72ed' },
      { id: 'pink', label: 'Розовый', value: '#f481df' },
      { id: 'coral', label: 'Коралловый', value: '#ff6969' },
    ],
  },
  {
    id: 'price',
    title: 'Цена',
    variant: 'stack',
    options: [
      { id: '0-1000', label: '0Р-1000Р' },
      { id: '1000-2000', label: '1000Р-2000Р' },
      { id: '2000-5000', label: '2000Р-5000Р' },
      { id: '5000-10000', label: '5000Р-10000Р' },
      { id: '10000-20000', label: '10000Р-20000Р' },
    ],
  },
  {
    id: 'brand',
    title: 'Бренд',
    variant: 'inline',
    isCollapsible: true,
    options: [
      { id: 'minimo', label: 'Minimo' },
      { id: 'retrio-brook', label: 'Retrio Brook' },
      { id: 'learts', label: 'Learts' },
      { id: 'vagabond', label: 'Vagabond' },
      { id: 'abby', label: 'Abby' },
    ],
  },
  {
    id: 'shape',
    title: 'Форма',
    variant: 'stack',
    isCollapsible: true,
    options: [
      { id: 'round', label: 'Круглая' },
      { id: 'square', label: 'Квадратная' },
      { id: 'oval', label: 'Овальная' },
    ],
  },
  {
    id: 'material',
    title: 'Материал',
    variant: 'stack',
    isCollapsible: true,
    options: [
      { id: 'all', label: 'Все материалы' },
      { id: 'acetate', label: '...' },
      { id: 'metal', label: '...' },
      { id: 'combined', label: '...' },
    ],
  },
];

export const catalogFiltersByCategory: Record<string, CatalogFilterGroup[]> = {
  frames: [
    {
      id: 'age',
      title: 'Возрастные группы',
      variant: 'inline',
      options: [
        { id: 'adult', label: 'Взрослый' },
        { id: 'teen', label: 'Подросток' },
        { id: 'child', label: 'Ребёнок' },
      ],
    },
    {
      id: 'gender',
      title: 'Пол',
      variant: 'inline',
      options: [
        { id: 'male', label: 'Мужской' },
        { id: 'female', label: 'Женский' },
        { id: 'unisex', label: 'Унисекс' },
      ],
    },
    ...baseCatalogFilterGroups,
  ],
  lenses: [
    {
      id: 'design',
      title: 'Дизайн',
      variant: 'stack',
      isCollapsible: true,
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
      variant: 'stack',
      isCollapsible: true,
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
      variant: 'stack',
      isCollapsible: true,
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
      variant: 'stack',
      isCollapsible: true,
      options: [
        { id: 'none', label: 'Без покрытия' },
        { id: 'protect-ar-plus', label: 'ProtectAR+' },
        { id: 'protect-ar-blue', label: 'ProtectAR+Blue' },
        { id: 'protect-ar-drive', label: 'ProtectAR+Drive' },
      ],
    },
  ],
  contacts: [
    {
      id: 'replacement-period',
      title: 'Срок замены',
      variant: 'stack',
      isCollapsible: true,
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
      variant: 'stack',
      isCollapsible: true,
      options: [
        { id: '8.4', label: '8.4' },
        { id: '8.5', label: '8.5' },
      ],
    },

    {
      id: 'material',
      title: 'Материал',
      variant: 'stack',
      isCollapsible: true,
      options: [
        { id: 'hydrogel', label: 'Гидрогель' },
        { id: 'silicone-hydrogel', label: 'Селиконгидрогель' },
      ],
    },
  ],
  accessories: [
    {
      id: 'sizes',
      title: 'Размер',
      variant: 'size',
      isCollapsible: true,
      options: [
        { id: 'small', label: 'S' },
        { id: 'medium', label: 'M' },
        { id: 'large', label: 'L' },
        { id: 'extra_large', label: 'XL' },
      ],
    },
    ...baseCatalogFilterGroups,
  ],
};
