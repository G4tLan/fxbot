import { taskService } from '$lib/api/task.service';
import type { BacktestResponse, ImportResponse, Task } from '$lib/api/types-helper';
import { writable } from 'svelte/store';
import { toastStore } from './toast.store';

interface TaskState {
  tasks: Record<string, Task>;
}

function createTaskStore() {
  const { subscribe, update } = writable<TaskState>({ tasks: {} });

  const pollTask = async (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const task = await taskService.getTask(taskId);
        update((s) => ({
          tasks: { ...s.tasks, [taskId]: task },
        }));

        const s = task.status.toLowerCase();
        if (s === 'completed' || s === 'success' || s === 'finished') {
          clearInterval(interval);
          toastStore.success(`Task ${taskId} completed successfully`);
        } else if (s === 'failed' || s === 'failure' || s === 'error') {
          clearInterval(interval);
          toastStore.error(`Task ${taskId} failed: ${task.error}`);
        }
      } catch (error) {
        console.error(`Failed to poll task ${taskId}`, error);
        clearInterval(interval);
      }
    }, 2000); // Poll every 2 seconds
  };

  return {
    subscribe,
    addImportTask: (response: ImportResponse) => {
      const task: Task = {
        id: response.task_id,
        status: response.status,
        type: 'import',
        created_at: Date.now() / 1000,
        updated_at: Date.now() / 1000,
      };
      update((s) => ({
        tasks: { ...s.tasks, [task.id]: task },
      }));
      pollTask(task.id);
    },
    addBacktestTask: (response: BacktestResponse) => {
      if (!response.task_id) return;

      const task: Task = {
        id: response.task_id,
        status: response.status,
        type: 'backtest',
        created_at: Date.now() / 1000,
        updated_at: Date.now() / 1000,
      };
      update((s) => ({
        tasks: { ...s.tasks, [task.id]: task },
      }));
      pollTask(task.id);
    },
    loadTasks: async () => {
      try {
        const tasks = await taskService.listTasks();
        const taskMap = tasks.reduce((acc, task) => ({ ...acc, [task.id]: task }), {});
        update((s) => ({ tasks: taskMap }));
      } catch (error) {
        console.error('Failed to load tasks', error);
      }
    },
  };
}

export const taskStore = createTaskStore();
