import type { PaginatedResponse, PaginationParams } from '@/shared/api';

export type News = {
  id: number;
  title: string;
  title_ru?: string | null;
  title_en?: string | null;
  title_uz?: string | null;
  image: string;
  text: string;
  text_ru?: string | null;
  text_en?: string | null;
  text_uz?: string | null;
  created_at?: string;
};

export type NewsParams = PaginationParams;

export type NewsResponse = PaginatedResponse<News>;
