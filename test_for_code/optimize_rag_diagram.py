#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG流程图优化Demo

读取example.drawio文件并将其优化为精美的RAG流程图
"""

import os
from drawio_editor import DrawIOEditor

# 定义RAG流程图的节点样式
STYLES = {
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
}

def create_rag_diagram():
    """创建优化的RAG流程图"""
    # 文件路径
    input_path = os.path.join(os.path.dirname(__file__), 'example.drawio')
    output_path = os.path.join(os.path.dirname(__file__), 'rag_optimized.drawio')
    
    # 初始化编辑器
    editor = DrawIOEditor(file_path=input_path)
    
    # 清除现有内容（保留根节点）
    nodes = editor.get_all_nodes()
    edges = editor.get_all_edges()
    
    # 删除所有边和非根节点
    for edge in edges:
        editor.delete_element(edge['id'])
    
    for node in nodes:
        if node['id'] not in ['0', '1']:
            editor.delete_element(node['id'])
    
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
    
    # 保存优化后的图表
    editor.save(output_path)
    print(f"优化后的RAG流程图已保存至: {output_path}")
    return output_path

def main():
    """主函数"""
    create_rag_diagram()

if __name__ == "__main__":
    main()