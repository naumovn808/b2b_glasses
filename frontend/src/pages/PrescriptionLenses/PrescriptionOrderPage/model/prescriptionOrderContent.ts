import type { DropdownOption } from '@/shared/ui';

export const salonOptions: DropdownOption[] = [
  { label: 'Hikari, Эски Саракуль 83', value: 'hikari-sarakul' },
  { label: 'Hikari, Миробод', value: 'hikari-mirobod' },
  { label: 'Hikari, центр города', value: 'hikari-center' },
];

export const deliveryOptions: DropdownOption[] = [
  { label: 'Самовывоз из салона', value: 'pickup' },
  { label: 'Доставка по Ташкенту', value: 'delivery-tashkent' },
  { label: 'Доставка курьером', value: 'courier' },
];

export const lensTypeOptions: DropdownOption[] = [
  { label: 'Однофокальные', value: 'single-vision' },
  { label: 'Прогрессивные', value: 'progressive' },
  { label: 'Офисные', value: 'office' },
  { label: 'Для вождения', value: 'drive' },
];
