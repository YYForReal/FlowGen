import { ChatMessage, DiagramState } from './components';

export interface ChatStore {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

export interface DiagramStore extends DiagramState {
  createDiagram: (prompt: string) => Promise<void>;
  updateDiagram: (xml: string) => Promise<void>;
  clearDiagram: () => void;
} 