import type { PaginatedResponse, PaginationParams } from '@/shared/api';

export type FAQ = {
  id: number;
  question: string;
  question_ru?: string | null;
  question_en?: string | null;
  question_uz?: string | null;
  answer: string;
  answer_ru?: string | null;
  answer_en?: string | null;
  answer_uz?: string | null;
  order?: number;
};

export type FaqParams = PaginationParams;

export type FaqResponse = PaginatedResponse<FAQ>;
