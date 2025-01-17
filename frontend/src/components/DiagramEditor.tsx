import { useEffect, useRef, useState } from 'react';
import { PlantUMLRenderer } from './PlantUMLRenderer';

interface DiagramEditorProps {
  className?: string;
  diagramType?: 'drawio' | 'plantuml';
  initialXml?: string;
  onXmlChange?: (xml: string) => void;
}

export function DiagramEditor({ 
  className,
  diagramType = 'drawio',
  initialXml = '',
  onXmlChange
}: DiagramEditorProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [xml, setXml] = useState(initialXml);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe || diagramType !== 'drawio') return;

    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.event === 'xmlUpdated') {
        const newXml = event.data.xml;
        setXml(newXml);
        onXmlChange?.(newXml);
      }
    };

    window.addEventListener('message', handleMessage);
    setIsLoading(false);

    return () => window.removeEventListener('message', handleMessage);
  }, [diagramType, onXmlChange]);

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  if (diagramType === 'plantuml') {
    return <PlantUMLRenderer code={xml} className={className} />;
  }

  return (
    <iframe
      ref={iframeRef}
      src="/drawio/index.html?embed=1&spin=1&analytics=0&links=0"
      className={`w-full h-full border-0 ${className}`}
      onLoad={() => {
        const iframe = iframeRef.current;
        if (iframe && iframe.contentWindow) {
          iframe.contentWindow.postMessage({ action: 'load', xml }, '*');
        }
      }}
    />
  );
} 