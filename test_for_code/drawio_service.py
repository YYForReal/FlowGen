#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DrawIO服务类

提供基于用户需求和现有DrawIO文件，自动生成和执行代码来优化图表的服务
"""

import os
import asyncio
import tempfile
from typing import Dict, Optional, Any, Tuple

from prompt import get_code_generation_prompt, get_diagram_generation_prompt
from drawio_editor import DrawIOEditor
from utils.execute_code import execute_code

class DrawIOService:
    """
    DrawIO服务类
    
    提供基于用户需求和现有DrawIO文件，自动生成和执行代码来优化图表的服务
    """
    
    def __init__(self, llm_service=None):
        """
        初始化DrawIO服务
        
        Args:
            llm_service: 大语言模型服务，用于生成代码
        """
        self.llm_service = llm_service
    
    async def optimize_diagram(self, 
                         user_requirement: str, 
                         diagram_type: str = None, 
                         current_drawio: Optional[str] = None,
                         input_path: Optional[str] = None,
                         output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        根据用户需求优化DrawIO图表
        
        Args:
            user_requirement: 用户需求描述
            diagram_type: 图表类型，如flowchart, er_diagram等
            current_drawio: 当前的DrawIO XML内容字符串（如果提供）
            input_path: 输入文件路径（如果提供）
            output_path: 输出文件路径（如果提供）
            
        Returns:
            包含优化结果的字典
        """
        # 1. 生成提示词
        prompt = get_code_generation_prompt(
            user_requirement=user_requirement,
            diagram_type=diagram_type,
            current_drawio=current_drawio
        )
        
        # 2. 调用大模型生成代码
        if self.llm_service:
            code = await self.llm_service.generate_code(prompt)
        else:
            # 如果没有提供LLM服务，使用示例代码（仅用于测试）
            code = self._generate_example_code(user_requirement, diagram_type, current_drawio, input_path, output_path)
        
        # 3. 执行生成的代码
        result = await self._execute_diagram_code(code, current_drawio, input_path, output_path)
        
        return result
    
    async def _execute_diagram_code(self, 
                              code: str, 
                              current_drawio: Optional[str] = None,
                              input_path: Optional[str] = None,
                              output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        执行生成的图表代码
        
        Args:
            code: 要执行的Python代码
            current_drawio: 当前的DrawIO XML内容字符串
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            包含执行结果的字典
        """
        # 创建临时文件用于输入和输出
        temp_dir = tempfile.mkdtemp()
        
        # 如果提供了current_drawio但没有input_path，创建临时输入文件
        if current_drawio and not input_path:
            input_path = os.path.join(temp_dir, "input.drawio")
            with open(input_path, "w", encoding="utf-8") as f:
                f.write(current_drawio)
        
        # 如果没有提供output_path，创建临时输出文件
        if not output_path:
            output_path = os.path.join(temp_dir, "output.drawio")
        
        # 修改代码，添加输入和输出路径
        modified_code = self._prepare_code_for_execution(code, input_path, output_path)
        
        # 执行代码
        success, output = await execute_code(modified_code)
        
        result = {
            "success": success,
            "message": output,
            "code": code,
            "output_path": output_path,
        }
        
        # 如果执行成功，读取生成的图表
        if success and os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    result["drawio_content"] = f.read()
            except Exception as e:
                result["success"] = False
                result["message"] = f"读取输出文件失败: {str(e)}"
        
        return result
    
    def _prepare_code_for_execution(self, code: str, input_path: Optional[str], output_path: str) -> str:
        """
        准备代码用于执行，添加必要的输入和输出路径
        
        Args:
            code: 原始代码
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            修改后的代码
        """
        # 导入必要的库
        imports = """
import os
from drawio_editor import DrawIOEditor
"""
        
        # 添加主函数调用，确保代码能够执行
        main_call = f"""

# 设置输入和输出路径
input_path = "{input_path}" if "{input_path}" else None
output_path = "{output_path}"

# 确保输出目录存在
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 执行主函数
if __name__ == "__main__":
    try:
        if "main" in globals():
            main()
        elif "create_diagram" in globals():
            create_diagram()
        elif "optimize_diagram" in globals():
            optimize_diagram()
        else:
            # 尝试找到并执行主要函数
            for func_name in globals():
                if callable(globals()[func_name]) and not func_name.startswith("_"):
                    globals()[func_name]()
                    break
    except Exception as e:
        print(f"执行出错: {{str(e)}}")
"""
        
        # 检查代码中是否已经包含了输入和输出路径的设置
        if "input_path" not in code and input_path:
            code = code.replace("def main():", f"def main():\n    # 设置输入路径\n    input_path = \"{input_path}\"\n")
        
        if "output_path" not in code:
            code = code.replace("def main():", f"def main():\n    # 设置输出路径\n    output_path = \"{output_path}\"\n")
        
        # 如果代码中没有导入必要的库，添加导入语句
        if "import os" not in code:
            code = imports + code
        
        # 如果代码中没有主函数调用，添加主函数调用
        if "__name__ == \"__main__\"" not in code:
            code += main_call
        
        return code
    
    def _generate_example_code(self, 
                           user_requirement: str, 
                           diagram_type: str, 
                           current_drawio: Optional[str],
                           input_path: Optional[str],
                           output_path: Optional[str]) -> str:
        """
        生成示例代码（仅用于测试，实际应用中应使用LLM服务）
        
        Args:
            user_requirement: 用户需求描述
            diagram_type: 图表类型
            current_drawio: 当前的DrawIO XML内容字符串
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            生成的示例代码
        """
        # 根据图表类型生成不同的示例代码
        if diagram_type == "flowchart":
            return self._generate_flowchart_example(input_path, output_path)
        elif diagram_type == "rag":
            return self._generate_rag_example(input_path, output_path)
        else:
            # 默认生成一个简单的图表
            return self._generate_simple_diagram_example(input_path, output_path)
    
    def _generate_flowchart_example(self, input_path: Optional[str], output_path: Optional[str]) -> str:
        """
        生成流程图示例代码
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            流程图示例代码
        """
        return f"""
import os
from drawio_editor import DrawIOEditor

# 定义流程图的节点样式
STYLES = {{
    'start': 'ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;',
    'process': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;',
    'decision': 'rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;',
    'end': 'ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=14;',
    'arrow': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;',
}}

def create_flowchart():
    # 初始化编辑器
    editor = DrawIOEditor()
    
    # 创建节点
    start_id = editor.add_node(
        text="开始",
        x=350,
        y=50,
        width=100,
        height=50,
        style=STYLES['start']
    )
    
    process1_id = editor.add_node(
        text="处理步骤1",
        x=350,
        y=150,
        width=120,
        height=60,
        style=STYLES['process']
    )
    
    decision_id = editor.add_node(
        text="判断条件",
        x=350,
        y=260,
        width=120,
        height=80,
        style=STYLES['decision']
    )
    
    process2_id = editor.add_node(
        text="处理步骤2",
        x=200,
        y=350,
        width=120,
        height=60,
        style=STYLES['process']
    )
    
    process3_id = editor.add_node(
        text="处理步骤3",
        x=500,
        y=350,
        width=120,
        height=60,
        style=STYLES['process']
    )
    
    end_id = editor.add_node(
        text="结束",
        x=350,
        y=450,
        width=100,
        height=50,
        style=STYLES['end']
    )
    
    # 添加连接线
    editor.add_edge(
        source_id=start_id,
        target_id=process1_id,
        style=STYLES['arrow']
    )
    
    editor.add_edge(
        source_id=process1_id,
        target_id=decision_id,
        style=STYLES['arrow']
    )
    
    editor.add_edge(
        source_id=decision_id,
        target_id=process2_id,
        label="是",
        style=STYLES['arrow']
    )
    
    editor.add_edge(
        source_id=decision_id,
        target_id=process3_id,
        label="否",
        style=STYLES['arrow']
    )
    
    editor.add_edge(
        source_id=process2_id,
        target_id=end_id,
        style=STYLES['arrow']
    )
    
    editor.add_edge(
        source_id=process3_id,
        target_id=end_id,
        style=STYLES['arrow']
    )
    
    # 保存图表
    output_path = "{output_path or 'flowchart_example.drawio'}"
    editor.save(output_path)
    print(f"流程图已保存至: {{output_path}}")
    return output_path

def main():
    create_flowchart()

if __name__ == "__main__":
    main()
"""
    
    def _generate_rag_example(self, input_path: Optional[str], output_path: Optional[str]) -> str:
        """
        生成RAG流程图示例代码
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            RAG流程图示例代码
        """
        return f"""
import os
from drawio_editor import DrawIOEditor

# 定义RAG流程图的节点样式
STYLES = {{
    # 数据源节点样式
    'data_source': 'shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;',
    # 检索节点样式
    'retrieval': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1',
    # 增强节点样式
    'augmentation': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=14;fontStyle=1',
    # 生成节点样式
    'generation': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=14;fontStyle=1',
    # 用户节点样式
    'user': 'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;fontSize=14;',
    # 文档节点样式
    'document': 'shape=document;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;fontSize=14;',
    # 连接线样式
    'arrow': 'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;fontSize=12;',
    # 虚线连接样式
    'dashed_arrow': 'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#6c8ebf;fontSize=12;dashed=1;'
}}

def create_rag_diagram():
    # 初始化编辑器
    editor = DrawIOEditor()
    
    # 创建RAG流程图节点
    # 1. 用户节点
    user_id = editor.add_node(
        text="用户",
        x=100,
        y=200,
        width=50,
        height=80,
        style=STYLES['user']
    )
    
    # 2. 数据源节点
    data_id = editor.add_node(
        text="知识库/文档",
        x=500,
        y=80,
        width=120,
        height=80,
        style=STYLES['data_source']
    )
    
    # 3. 检索节点
    retrieval_id = editor.add_node(
        text="检索 (Retrieval)",
        x=300,
        y=200,
        width=160,
        height=60,
        style=STYLES['retrieval']
    )
    
    # 4. 增强节点
    augmentation_id = editor.add_node(
        text="增强 (Augmentation)",
        x=500,
        y=200,
        width=160,
        height=60,
        style=STYLES['augmentation']
    )
    
    # 5. 生成节点
    generation_id = editor.add_node(
        text="生成 (Generation)",
        x=700,
        y=200,
        width=160,
        height=60,
        style=STYLES['generation']
    )
    
    # 6. 结果文档节点
    result_id = editor.add_node(
        text="回答结果",
        x=700,
        y=320,
        width=120,
        height=80,
        style=STYLES['document']
    )
    
    # 添加连接线
    # 用户 -> 检索
    editor.add_edge(
        source_id=user_id,
        target_id=retrieval_id,
        label="查询",
        style=STYLES['arrow']
    )
    
    # 检索 -> 数据源
    editor.add_edge(
        source_id=retrieval_id,
        target_id=data_id,
        label="检索相关文档",
        style=STYLES['arrow']
    )
    
    # 数据源 -> 增强
    editor.add_edge(
        source_id=data_id,
        target_id=augmentation_id,
        label="相关上下文",
        style=STYLES['arrow']
    )
    
    # 检索 -> 增强
    editor.add_edge(
        source_id=retrieval_id,
        target_id=augmentation_id,
        label="",
        style=STYLES['arrow']
    )
    
    # 增强 -> 生成
    editor.add_edge(
        source_id=augmentation_id,
        target_id=generation_id,
        label="增强后的上下文",
        style=STYLES['arrow']
    )
    
    # 生成 -> 结果
    editor.add_edge(
        source_id=generation_id,
        target_id=result_id,
        label="",
        style=STYLES['arrow']
    )
    
    # 结果 -> 用户
    editor.add_edge(
        source_id=result_id,
        target_id=user_id,
        label="返回回答",
        style=STYLES['dashed_arrow']
    )
    
    # 保存图表
    output_path = "{output_path or 'rag_example.drawio'}"
    editor.save(output_path)
    print(f"RAG流程图已保存至: {{output_path}}")
    return output_path

def main():
    create_rag_diagram()

if __name__ == "__main__":
    main()
"""
    
    def _generate_simple_diagram_example(self, input_path: Optional[str], output_path: Optional[str]) -> str:
        """
        生成简单图表示例代码
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            简单图表示例代码
        """
        return f"""
import os
from drawio_editor import DrawIOEditor

# 定义基本样式
STYLES = {{
    'node': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;fontSize=14;',
    'special_node': 'ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;',
    'arrow': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;'
}}

def create_simple_diagram():
    # 初始化编辑器
    editor = DrawIOEditor()
    
    # 创建节点
    node1_id = editor.add_node(
        text="节点1",
        x=200,
        y=150,
        width=120,
        height=60,
        style=STYLES['node']
    )
    
    node2_id = editor.add_node(
        text="节点2",
        x=400,
        y=150,
        width=120,
        height=60,
        style=STYLES['node']
    )
    
    node3_id = editor.add_node(
        text="特殊节点",
        x=300,
        y=300,
        width=120,
        height=80,
        style=STYLES['special_node']
    )
    
    # 添加连接线
    editor.add_edge(
        source_id=node1_id,
        target_id=node2_id,
        label="连接",
        style=STYLES['arrow']
    )
    
    editor.add_edge(
        source_id=node1_id,
        target_id=node3_id,
        label="关联1",
        style=STYLES['arrow']
    )
    
    editor.add_edge(
        source_id=node2_id,
        target_id=node3_id,
        label="关联2",
        style=STYLES['arrow']
    )
    
    # 保存图表
    output_path = "{output_path or 'simple_diagram.drawio'}"
    editor.save(output_path)
    print(f"简单图表已保存至: {{output_path}}")
    return output_path

def main():
    create_simple_diagram()

if __name__ == "__main__":
    main()
"""