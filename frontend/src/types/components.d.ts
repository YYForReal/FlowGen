import { ReactNode } from 'react';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface ChatPanelProps {
  className?: string;
  children?: ReactNode;
}

export interface DiagramEditorProps {
  className?: string;
  children?: ReactNode;
}

export interface ChatFormProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
}

export interface DiagramState {
  xml: string | null;
  png: string | null;
  isLoading: boolean;
  error: string | null;
} 