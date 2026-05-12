export {
  trainingApi,
  useGetTrainingByIdQuery,
  useGetTrainingQuery,
} from './api/trainingApi';
export { selectTrainingById } from './model/selectors';
export type { TrainingCacheRootState } from './model/selectors';
export type { Training, TrainingParams, TrainingResponse } from './model/types';
