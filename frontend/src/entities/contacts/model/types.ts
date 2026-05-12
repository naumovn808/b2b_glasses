export type Contacts = {
  id: number;
  phone: string;
  email: string;
  address_label: string;
  address_label_ru?: string | null;
  address_label_en?: string | null;
  address_label_uz?: string | null;
  address_link?: string | null;
  work_hours: string;
  work_hours_ru?: string | null;
  work_hours_en?: string | null;
  work_hours_uz?: string | null;
};
