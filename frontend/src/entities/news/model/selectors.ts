import { newsApi } from '../api/newsApi';
import type { News } from './types';

export type NewsCacheRootState = Parameters<
  ReturnType<typeof newsApi.endpoints.getNews.select>
>[0];

export function selectNewsById(
  state: NewsCacheRootState,
  newsId?: string,
): News | undefined {
  if (!newsId) {
    return undefined;
  }

  return newsApi.endpoints.getNews
    .select()(state)
    .data?.results.find((news) => String(news.id) === newsId);
}
