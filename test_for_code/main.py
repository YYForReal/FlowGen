#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DrawIO图表生成与优化服务主程序

提供基于用户需求和现有DrawIO文件，自动生成和执行代码来优化图表的服务
"""

import os
import asyncio
import argparse
from typing import Optional, Dict, Any

from drawio_service import DrawIOService
from llm.dash_deepseek import DeepseekLLM

# 使用DeepseekLLM服务
class DeepseekLLMService:
    """
    基于DeepseekLLM的大语言模型服务
    
    使用DeepseekLLM进行代码生成
    """
    def __init__(self):
        """
        初始化DeepseekLLM服务
        """
        self.llm = DeepseekLLM()
        
    async def generate_code(self, prompt: str) -> str:
        """
        使用DeepseekLLM生成代码
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的代码
        """
        response = self.llm.chat(prompt)
        return response.answer_content or """
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from drawio_editor import DrawIOEditor

def create_diagram():
    # 初始化编辑器
    editor = DrawIOEditor()
    
    # 创建节点
    node1_id = editor.add_node(
        text="节点1",
        x=200,
        y=150,
        width=120,
        height=60,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
    )
    
    node2_id = editor.add_node(
        text="节点2",
        x=400,
        y=150,
        width=120,
        height=60,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
    )
    
    # 添加连接线
    editor.add_edge(
        source_id=node1_id,
        target_id=node2_id,
        label="连接",
        style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    )
    
    # 保存图表
    output_path = "output.drawio"
    editor.save(output_path)
    print(f"图表已保存至: {output_path}")
    return output_path

def main():
    create_diagram()

if __name__ == "__main__":
    main()
"""

async def main():
    """
    主函数，处理命令行参数并执行图表生成或优化
    """
    parser = argparse.ArgumentParser(description="DrawIO图表生成与优化服务")
    parser.add_argument("--requirement", "-r", type=str, help="用户需求描述")
    parser.add_argument("--type", "-t", type=str, help="图表类型，如flowchart, er_diagram, rag等")
    parser.add_argument("--input", "-i", type=str, help="输入文件路径（可选）")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径（可选）")
    
    args = parser.parse_args()
    
    # 如果没有提供用户需求，使用交互式输入
    if not args.requirement:
        print("请输入您的图表需求描述：")
        requirement = input("> ")
    else:
        requirement = args.requirement
    
    # 如果没有提供图表类型，使用交互式输入
    if not args.type:
        print("请输入图表类型（如flowchart, er_diagram, rag等，直接回车使用默认类型）：")
        diagram_type = input("> ") or None
    else:
        diagram_type = args.type
    
    # 如果提供了输入文件，读取文件内容
    current_drawio = None
    if args.input and os.path.exists(args.input):
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                current_drawio = f.read()
            print(f"已读取输入文件: {args.input}")
        except Exception as e:
            print(f"读取输入文件失败: {str(e)}")
    
    # 创建服务实例
    llm_service = DeepseekLLMService()  # 使用DeepseekLLM服务
    service = DrawIOService(llm_service=llm_service)
    
    # 执行图表优化
    print("正在处理您的需求，请稍候...")
    result = await service.optimize_diagram(
        user_requirement=requirement,
        diagram_type=diagram_type,
        current_drawio=current_drawio,
        input_path=args.input,
        output_path=args.output
    )
    
    # 输出结果
    if result["success"]:
        print(f"处理成功！图表已保存至: {result['output_path']}")
    else:
        print(f"处理失败: {result['message']}")
    
    # 输出生成的代码（可选）
    print("\n生成的代码：")
    print("="*80)
    print(result["code"])
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())