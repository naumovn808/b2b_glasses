import type { Training } from './types';
import { trainingApi } from '../api/trainingApi';

export type TrainingCacheRootState = Parameters<
  ReturnType<typeof trainingApi.endpoints.getTraining.select>
>[0];

export function selectTrainingById(
  state: TrainingCacheRootState,
  trainingId?: string,
): Training | undefined {
  if (!trainingId) {
    return undefined;
  }

  return trainingApi.endpoints.getTraining
    .select()(state)
    .data?.results.find((training) => String(training.id) === trainingId);
}
