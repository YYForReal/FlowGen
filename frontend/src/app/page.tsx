'use client';

import { useState } from 'react';
import { ChatPanel } from '@/components/ChatPanel';
import { DiagramEditor } from '@/components/DiagramEditor';

export default function Home() {
  const [currentDiagram, setCurrentDiagram] = useState<{
    type: 'drawio' | 'plantuml';
    xml: string;
  } | null>(null);

  return (
    <main className="flex min-h-screen bg-white">
      <div className="w-1/2 border-r border-gray-200">
        <ChatPanel 
          className="h-full" 
          onDiagramChange={setCurrentDiagram}
        />
      </div>
      <div className="w-1/2">
        <DiagramEditor 
          className="h-full"
          diagramType={currentDiagram?.type}
          initialXml={currentDiagram?.xml}
        />
      </div>
    </main>
  );
}
