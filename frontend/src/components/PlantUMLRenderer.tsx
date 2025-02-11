import { useEffect, useState } from 'react';
import pako from 'pako';

interface PlantUMLRendererProps {
  code: string;
  className?: string;
}

export function PlantUMLRenderer({ code, className }: PlantUMLRendererProps) {
  const [imageUrl, setImageUrl] = useState<string>('');

  useEffect(() => {
    if (!code) return;

    // 这里使用 PlantUML 在线服务器进行渲染
    // 实际项目中建议使用自己的服务器
    const encodedCode = encode64(deflate(code));
    setImageUrl(`https://www.plantuml.com/plantuml/img/${encodedCode}`);
  }, [code]);

  if (!imageUrl) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div className="text-gray-500">等待生成图表...</div>
      </div>
    );
  }

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <img src={imageUrl} alt="PlantUML Diagram" className="max-w-full max-h-full" />
    </div>
  );
}

// PlantUML 编码函数
function encode64(data: string) {
  let r = "";
  for (let i=0; i < data.length; i += 3) {
    if (i + 2 == data.length) {
      r += append3bytes(data.charCodeAt(i), data.charCodeAt(i+1), 0);
    } else if (i + 1 == data.length) {
      r += append3bytes(data.charCodeAt(i), 0, 0);
    } else {
      r += append3bytes(data.charCodeAt(i), data.charCodeAt(i+1), data.charCodeAt(i+2));
    }
  }
  return r;
}

function append3bytes(b1: number, b2: number, b3: number) {
  const c1 = b1 >> 2;
  const c2 = ((b1 & 0x3) << 4) | (b2 >> 4);
  const c3 = ((b2 & 0xF) << 2) | (b3 >> 6);
  const c4 = b3 & 0x3F;
  let r = "";
  r += encode6bit(c1 & 0x3F);
  r += encode6bit(c2 & 0x3F);
  r += encode6bit(c3 & 0x3F);
  r += encode6bit(c4 & 0x3F);
  return r;
}

function encode6bit(b: number) {
  if (b < 10) return String.fromCharCode(48 + b);
  b -= 10;
  if (b < 26) return String.fromCharCode(65 + b);
  b -= 26;
  if (b < 26) return String.fromCharCode(97 + b);
  b -= 26;
  if (b === 0) return '-';
  if (b === 1) return '_';
  return '?';
}

// PlantUML 压缩函数
function deflate(str: string): string {
  // 将字符串转换为 UTF-8 编码的 Uint8Array
  const utf8Encoder = new TextEncoder();
  const data = utf8Encoder.encode(str);
  
  // 使用 pako 进行压缩
  const compressed = pako.deflate(data, { level: 9 });
  
  // 将压缩后的数据转换为字符串
  return String.fromCharCode.apply(null, compressed);
} 