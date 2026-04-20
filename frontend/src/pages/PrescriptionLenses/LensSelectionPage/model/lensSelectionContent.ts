import type { DropdownOption } from '@/shared/ui';

export const manufacturerTags = ['BBRG', 'Lencor vision'];
export const indexTags = ['15', '153', '156', '159', '16', '167', '174'];

export const lensTypeOptions: DropdownOption[] = [
  { label: 'Однофокальные', value: 'single-vision' },
  { label: 'Прогрессивные', value: 'progressive' },
  { label: 'Офисные', value: 'office' },
  { label: 'Для вождения', value: 'drive' },
];

export const lensDesignOptions: DropdownOption[] = [
  { label: 'Сферический', value: 'spherical' },
  { label: 'Асферический', value: 'aspherical' },
  { label: 'Индивидуальный', value: 'individual' },
];

export const coatingOptions: DropdownOption[] = [
  { label: 'Антиблик', value: 'anti-reflective' },
  { label: 'Упрочняющее', value: 'hard-coat' },
  { label: 'Blue block', value: 'blue-block' },
];

export const propertyOptions: DropdownOption[] = [
  { label: 'Тонкие', value: 'thin' },
  { label: 'Фотохромные', value: 'photochromic' },
  { label: 'Поляризационные', value: 'polarized' },
];

export const colorOptions: DropdownOption[] = [
  { label: 'Прозрачный', value: 'clear' },
  { label: 'Серый', value: 'gray' },
  { label: 'Коричневый', value: 'brown' },
  { label: 'Зеленый', value: 'green' },
];
