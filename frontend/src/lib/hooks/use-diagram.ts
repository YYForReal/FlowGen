import { create } from 'zustand';
import { DiagramStore, ApiResponse, DiagramUpdateResponse } from '@/types';
import { StateCreator } from 'zustand';

type DiagramStoreState = Omit<DiagramStore, 'createDiagram' | 'updateDiagram' | 'clearDiagram'>;
type DiagramStoreActions = Pick<DiagramStore, 'createDiagram' | 'updateDiagram' | 'clearDiagram'>;

const createDiagramStore: StateCreator<DiagramStore> = (set) => ({
  xml: null,
  png: null,
  isLoading: false,
  error: null,

  createDiagram: async (prompt: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch('/api/diagram/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      const data: ApiResponse<DiagramUpdateResponse> = await response.json();

      if (!data.success || !data.data) {
        throw new Error(data.error || '创建图表失败');
      }

      set({
        xml: data.data.xml,
        png: data.data.png,
        isLoading: false,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '未知错误',
      });
    }
  },

  updateDiagram: async (xml: string) => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch('/api/diagram/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ xml }),
      });

      const data: ApiResponse<DiagramUpdateResponse> = await response.json();

      if (!data.success || !data.data) {
        throw new Error(data.error || '更新图表失败');
      }

      set({
        xml: data.data.xml,
        png: data.data.png,
        isLoading: false,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '未知错误',
      });
    }
  },

  clearDiagram: () => {
    set({
      xml: null,
      png: null,
      error: null,
    });
  },
});

export const useDiagram = create<DiagramStore>(createDiagramStore); 