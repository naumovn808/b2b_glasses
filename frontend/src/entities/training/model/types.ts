import type { PaginatedResponse, PaginationParams } from '@/shared/api';

export type Training = {
  id: number;
  title: string;
  title_ru?: string | null;
  title_en?: string | null;
  title_uz?: string | null;
  image: string;
  video?: string | null;
  description: string;
  description_ru?: string | null;
  description_en?: string | null;
  description_uz?: string | null;
  order?: number;
};

export type TrainingParams = PaginationParams;

export type TrainingResponse = PaginatedResponse<Training>;
