#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DrawIO文件生成提示模板

提供用于提示大模型生成DrawIO文件操作代码的模板
"""

from typing import Optional, Dict, Any, List

# DrawIO文件常见节点类型及其样式模板
NODE_STYLES = {
    # 基础形状
    'rectangle': 'rounded=0;whiteSpace=wrap;html=1;',
    'rounded_rectangle': 'rounded=1;whiteSpace=wrap;html=1;',
    'circle': 'ellipse;whiteSpace=wrap;html=1;aspect=fixed;',
    'ellipse': 'ellipse;whiteSpace=wrap;html=1;',
    'diamond': 'rhombus;whiteSpace=wrap;html=1;',
    'triangle': 'triangle;whiteSpace=wrap;html=1;',
    'hexagon': 'shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;',
    
    # 特殊形状
    'cylinder': 'shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;',
    'cloud': 'ellipse;shape=cloud;whiteSpace=wrap;html=1;',
    'document': 'shape=document;whiteSpace=wrap;html=1;boundedLbl=1;',
    'actor': 'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;',
    'note': 'shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;darkOpacity=0.05;',
    
    # 流程图专用
    'process': 'rounded=1;whiteSpace=wrap;html=1;',
    'decision': 'rhombus;whiteSpace=wrap;html=1;',
    'terminator': 'ellipse;whiteSpace=wrap;html=1;',
    'data': 'shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;',
    'predefined_process': 'shape=process;whiteSpace=wrap;html=1;backgroundOutline=1;',
    'database': 'shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;',
    
    # 连接线样式
    'arrow': 'endArrow=classic;html=1;rounded=0;',
    'dashed_arrow': 'endArrow=classic;html=1;rounded=0;dashed=1;',
    'bidirectional_arrow': 'endArrow=classic;startArrow=classic;html=1;rounded=0;',
    'orthogonal_arrow': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;',
    'curved_arrow': 'edgeStyle=entityRelationEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;',
}

# 常用颜色样式
COLOR_STYLES = {
    'blue': 'fillColor=#dae8fc;strokeColor=#6c8ebf;',
    'green': 'fillColor=#d5e8d4;strokeColor=#82b366;',
    'yellow': 'fillColor=#fff2cc;strokeColor=#d6b656;',
    'orange': 'fillColor=#ffe6cc;strokeColor=#d79b00;',
    'red': 'fillColor=#f8cecc;strokeColor=#b85450;',
    'purple': 'fillColor=#e1d5e7;strokeColor=#9673a6;',
    'gray': 'fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;',
}

# 文本样式
TEXT_STYLES = {
    'bold': 'fontStyle=1;',
    'italic': 'fontStyle=2;',
    'bold_italic': 'fontStyle=3;',
    'underline': 'fontStyle=4;',
    'small': 'fontSize=8;',
    'normal': 'fontSize=12;',
    'large': 'fontSize=16;',
    'xlarge': 'fontSize=24;',
}

# 常见图表类型及其描述
DIAGRAM_TYPES = {
    'flowchart': '流程图 - 展示过程、决策和工作流',
    'er_diagram': '实体关系图 - 展示数据库表和关系',
    'uml_class': 'UML类图 - 展示类、属性、方法和关系',
    'uml_sequence': 'UML序列图 - 展示对象间的交互顺序',
    'mindmap': '思维导图 - 展示分层的概念和想法',
    'org_chart': '组织结构图 - 展示层级关系',
    'network': '网络图 - 展示节点和连接',
    'rag': 'RAG流程图 - 展示检索增强生成的流程',
}

def get_diagram_generation_prompt(user_requirement: str, diagram_type: str = None, current_drawio: Optional[str] = None) -> str:
    """
    生成用于提示大模型创建或修改DrawIO图表的提示词
    
    Args:
        user_requirement: 用户的图表需求描述
        diagram_type: 图表类型，如flowchart, er_diagram等
        current_drawio: 当前的DrawIO XML内容字符串（如果是修改现有图表）
        
    Returns:
        用于提示大模型的提示词字符串
    """
    diagram_type_desc = DIAGRAM_TYPES.get(diagram_type, '通用图表') if diagram_type else '通用图表'
    
    prompt = f"""
你是一个专业的图表生成助手，请根据以下需求生成Python代码，该代码使用DrawIOEditor类来创建或修改DrawIO图表。

## 用户需求
{user_requirement}

## 图表类型
{diagram_type_desc}

## 当前图表内容
{"无现有图表" if current_drawio is None else "需要修改的现有图表"}

## 可用的工具类
你可以使用DrawIOEditor类来操作DrawIO图表，该类提供以下主要方法：

1. 初始化：`editor = DrawIOEditor(file_path=文件路径, content=XML内容字符串)`
2. 添加节点：`node_id = editor.add_node(text="节点文本", x=横坐标, y=纵坐标, width=宽度, height=高度, style=样式字符串)`
3. 添加连接线：`edge_id = editor.add_edge(source_id=源节点ID, target_id=目标节点ID, label="连接线文本", style=样式字符串)`
4. 更新节点：`editor.update_node(node_id=节点ID, text="新文本", style="新样式", x=新横坐标, y=新纵坐标, width=新宽度, height=新高度)`
5. 删除元素：`editor.delete_element(element_id=元素ID)`
6. 获取所有节点：`nodes = editor.get_all_nodes()`
7. 获取所有连接线：`edges = editor.get_all_edges()`
8. 保存图表：`editor.save(output_path=输出文件路径)`
9. 转换为字符串：`xml_string = editor.to_string()`

## 样式参考
你可以使用以下样式来美化图表：

### 节点样式
```python
STYLES = {{
    # 基本形状样式示例
    'rectangle': 'rounded=0;whiteSpace=wrap;html=1;',
    'rounded_rectangle': 'rounded=1;whiteSpace=wrap;html=1;',
    'circle': 'ellipse;whiteSpace=wrap;html=1;aspect=fixed;',
    'diamond': 'rhombus;whiteSpace=wrap;html=1;',
    
    # 特殊形状样式示例
    'cylinder': 'shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;',
    'document': 'shape=document;whiteSpace=wrap;html=1;boundedLbl=1;',
    'actor': 'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;',
    
    # 颜色样式示例
    'blue_fill': 'fillColor=#dae8fc;strokeColor=#6c8ebf;',
    'green_fill': 'fillColor=#d5e8d4;strokeColor=#82b366;',
    'orange_fill': 'fillColor=#ffe6cc;strokeColor=#d79b00;',
    'purple_fill': 'fillColor=#e1d5e7;strokeColor=#9673a6;',
    
    # 连接线样式示例
    'arrow': 'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;',
    'dashed_arrow': 'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;dashed=1;',
}}
```

## 输出要求
请生成一个完整的Python函数，该函数接收以下参数：
1. input_path: 输入文件路径（如果是修改现有图表）
2. output_path: 输出文件路径
3. content: DrawIO XML内容字符串（可选，如果提供则优先使用）

函数应返回生成或修改后的DrawIO XML内容字符串。

请确保代码可以直接执行，并包含必要的注释。不要包含任何无法执行的伪代码。
"""
    
    return prompt

def get_diagram_analysis_prompt(drawio_content: str) -> str:
    """
    生成用于提示大模型分析DrawIO图表的提示词
    
    Args:
        drawio_content: DrawIO XML内容字符串
        
    Returns:
        用于提示大模型的提示词字符串
    """
    prompt = f"""
你是一个专业的图表分析助手，请分析以下DrawIO图表的XML内容，并提供详细的结构描述。

## DrawIO XML内容
```xml
{drawio_content}
```

## 分析要求
1. 识别图表的类型（如流程图、ER图、UML图等）
2. 列出图表中的主要节点及其属性（文本、位置、样式等）
3. 描述节点之间的连接关系
4. 分析图表的整体结构和布局
5. 提出可能的改进建议

请以结构化的方式提供你的分析结果。
"""
    
    return prompt

def get_code_generation_prompt(user_requirement: str, diagram_type: str = None, current_drawio: Optional[str] = None) -> str:
    """
    生成用于提示大模型生成DrawIO操作代码的提示词
    
    Args:
        user_requirement: 用户的代码需求描述
        diagram_type: 图表类型，如flowchart, er_diagram等
        current_drawio: 当前的DrawIO XML内容字符串（如果是修改现有图表）
        
    Returns:
        用于提示大模型的提示词字符串
    """
    diagram_type_desc = DIAGRAM_TYPES.get(diagram_type, '通用图表') if diagram_type else '通用图表'
    
    prompt = f"""
你是一个专业的图表代码生成助手，请根据以下需求生成Python代码，该代码使用DrawIOEditor类来创建或修改DrawIO图表。

## 用户需求
{user_requirement}

## 图表类型
{diagram_type_desc}

## 当前图表内容
{"无现有图表" if current_drawio is None else "需要修改的现有图表"}

## 代码要求
1. 使用DrawIOEditor类来操作DrawIO图表
2. 代码应该清晰、模块化，并包含详细注释
3. 确保代码可以直接执行，不包含任何伪代码
4. 使用适当的样式和布局来创建美观的图表
5. 如果是修改现有图表，应该先分析现有结构，然后进行修改

## 输出格式
请生成一个完整的Python模块，包含以下内容：
1. 必要的导入语句
2. 样式定义（如果需要）
3. 主要的图表生成/修改函数
4. 辅助函数（如果需要）
5. 主函数和执行入口

请确保代码遵循PEP 8风格指南，并且可以直接执行。
"""
    
    return prompt

# 示例用法
if __name__ == "__main__":
    # 示例：生成图表生成提示词
    user_req = "创建一个展示微服务架构的系统架构图，包含API网关、服务发现、配置中心、各业务微服务和数据库"
    prompt = get_diagram_generation_prompt(user_req, diagram_type="network")