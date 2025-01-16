import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import { ChatStore, ChatMessage, ApiResponse, ChatCompletionResponse } from '@/types';
import { StateCreator } from 'zustand';

type ChatStoreState = Omit<ChatStore, 'addMessage' | 'sendMessage' | 'clearMessages'>;
type ChatStoreActions = Pick<ChatStore, 'addMessage' | 'sendMessage' | 'clearMessages'>;

const createChatStore: StateCreator<ChatStore> = (set, get) => ({
  messages: [],
  isLoading: false,
  error: null,

  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: uuidv4(),
      timestamp: Date.now(),
    };
    set((state: ChatStoreState) => ({
      messages: [...state.messages, newMessage],
    }));
  },

  sendMessage: async (content: string) => {
    const { addMessage } = get();
    set({ isLoading: true, error: null });

    try {
      addMessage({ role: 'user', content });

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content }),
      });

      const data: ApiResponse<ChatCompletionResponse> = await response.json();

      if (!data.success || !data.data) {
        throw new Error(data.error || '请求失败');
      }

      addMessage({
        role: 'assistant',
        content: data.data.message,
      });

      set({ isLoading: false });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : '未知错误',
      });
    }
  },

  clearMessages: () => {
    set({ messages: [], error: null });
  },
});

export const useChat = create<ChatStore>(createChatStore); 