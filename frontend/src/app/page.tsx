'use client';

import { ChatPanel } from '@/components/ChatPanel';
import { DiagramEditor } from '@/components/DiagramEditor';

export default function Home() {
  return (
    <main className="flex h-screen">
      <div className="w-1/2 border-r">
        <ChatPanel className="h-full" />
      </div>
      <div className="w-1/2">
        <DiagramEditor className="h-full" />
      </div>
    </main>
  );
}
