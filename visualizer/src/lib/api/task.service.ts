import { api } from './client';
import type { Task } from './types-helper';

export const taskService = {
  getTask: async (taskId: string) => {
    return api.get<Task>(`/api/v1/tasks/${taskId}`);
  },

  listTasks: async (limit: number = 10, offset: number = 0) => {
    return api.get<Task[]>(`/api/v1/tasks?limit=${limit}&offset=${offset}`);
  },
};
