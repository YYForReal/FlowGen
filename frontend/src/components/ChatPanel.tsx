import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  diagram?: {
    type: 'drawio' | 'plantuml';
    xml: string;
  };
}

interface ChatPanelProps {
  className?: string;
  onDiagramChange?: (diagram: { type: 'drawio' | 'plantuml'; xml: string }) => void;
}

export function ChatPanel({ className, onDiagramChange }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 模拟API响应
      const mockResponse: Message = {
        role: 'assistant',
        content: '我已经根据你的要求生成了一个示例图表。',
        diagram: {
          type: 'plantuml',
          xml: `@startuml
actor User
participant "Frontend" as F
participant "Backend" as B

User -> F: 输入绘图需求
F -> B: 发送请求
B -> B: 生成图表
B --> F: 返回图表数据
F --> User: 显示图表
@enduml`
        }
      };

      setMessages(prev => [...prev, mockResponse]);
      if (mockResponse.diagram) {
        onDiagramChange?.(mockResponse.diagram);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '抱歉，生成图表时出现错误。'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chat-message ${
              message.role === 'user'
                ? 'chat-message-user'
                : 'chat-message-assistant'
            }`}
          >
            <div className="mb-2">{message.content}</div>
            {message.diagram && (
              <div className="mt-2 p-2 bg-white rounded border">
                <pre className="text-sm overflow-x-auto scrollbar-hide">
                  {message.diagram.xml}
                </pre>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent" />
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="请描述你想要绘制的图表..."
            className="input-primary"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary"
          >
            发送
          </button>
        </div>
      </form>
    </div>
  );
} 