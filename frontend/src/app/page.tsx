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
    <main className="flex h-screen">
      <div className="w-1/2 border-r">
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
