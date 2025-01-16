import { useState } from 'react';
import { ChatPanelProps, ChatFormProps } from '@/types';
import { useChat } from '@/lib/hooks/use-chat';

const ChatForm = ({ onSubmit, disabled }: ChatFormProps) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSubmit(input);
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="输入你的想法..."
      />
      <button
        type="submit"
        disabled={disabled}
        className="px-4 py-2 text-white bg-blue-500 rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        发送
      </button>
    </form>
  );
};

export function ChatPanel({ className }: ChatPanelProps) {
  const { messages, isLoading, sendMessage } = useChat();

  return (
    <div className={`flex flex-col h-full ${className}`}>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t">
        <ChatForm onSubmit={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
} 