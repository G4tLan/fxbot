import { api } from './client';
import type { ImportRequest, ImportResponse } from './types-helper';

export const importService = {
  triggerImport: async (data: ImportRequest) => {
    return api.post<ImportResponse>('/api/v1/import', data);
  },
};
