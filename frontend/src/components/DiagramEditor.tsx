import { useEffect, useRef } from 'react';
import { DiagramEditorProps } from '@/types';
import { useDiagram } from '@/lib/hooks/use-diagram';

export function DiagramEditor({ className }: DiagramEditorProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const { xml, png, isLoading, error, updateDiagram } = useDiagram();

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.event === 'xmlUpdated') {
        updateDiagram(event.data.xml);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [updateDiagram]);

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

  if (!xml) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div className="text-gray-500">等待生成图表...</div>
      </div>
    );
  }

  return (
    <iframe
      ref={iframeRef}
      src="/drawio/index.html"
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