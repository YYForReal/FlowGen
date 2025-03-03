#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DrawIOEditor类扩展

提供对DrawIOEditor类的扩展功能，增加更多实用方法
"""

from typing import Dict, Optional, Any, List, Union
from drawio_editor import DrawIOEditor

class DrawIOEditorExtended(DrawIOEditor):
    """
    DrawIOEditor类的扩展，增加更多实用方法
    
    继承自DrawIOEditor类，提供额外的功能，如通过ID获取节点信息、批量操作等
    """
    
    def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        通过ID获取节点信息
        
        与find_element_by_id不同，此方法返回节点的完整信息字典，而不是XML元素
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点信息字典，如果未找到则返回None
        """
        element = self.find_element_by_id(node_id)
        if element is None or element.get('vertex') != '1':
            return None
        
        node_info = {
            'id': element.get('id'),
            'value': element.get('value', ''),
            'style': element.get('style', ''),
            'parent': element.get('parent', '')
        }
        
        # 获取几何信息
        geometry = element.find('./mxGeometry')
        if geometry is not None:
            node_info['x'] = geometry.get('x')
            node_info['y'] = geometry.get('y')
            node_info['width'] = geometry.get('width')
            node_info['height'] = geometry.get('height')
        
        return node_info
    
    def get_edge_by_id(self, edge_id: str) -> Optional[Dict[str, Any]]:
        """
        通过ID获取连接线信息
        
        Args:
            edge_id: 连接线ID
            
        Returns:
            连接线信息字典，如果未找到则返回None
        """
        element = self.find_element_by_id(edge_id)
        if element is None or element.get('edge') != '1':
            return None
        
        edge_info = {
            'id': element.get('id'),
            'value': element.get('value', ''),
            'style': element.get('style', ''),
            'parent': element.get('parent', ''),
            'source': element.get('source', ''),
            'target': element.get('target', '')
        }
        
        return edge_info
    
    def find_nodes_by_text(self, text: str, exact_match: bool = False) -> List[Dict[str, Any]]:
        """
        通过文本内容查找节点
        
        Args:
            text: 要查找的文本
            exact_match: 是否精确匹配，如果为False则使用包含匹配
            
        Returns:
            匹配的节点信息列表
        """
        nodes = []
        all_nodes = self.get_all_nodes()
        
        for node in all_nodes:
            node_text = node.get('value', '')
            if (exact_match and node_text == text) or (not exact_match and text in node_text):
                nodes.append(node)
        
        return nodes
    
    def batch_update_nodes(self, updates: List[Dict[str, Any]]) -> bool:
        """
        批量更新节点
        
        Args:
            updates: 更新信息列表，每个元素是一个包含node_id和更新属性的字典
            
        Returns:
            是否全部更新成功
        """
        success = True
        for update in updates:
            node_id = update.pop('node_id', None)
            if node_id:
                result = self.update_node(node_id=node_id, **update)
                success = success and result
        
        return success
    
    def get_connected_nodes(self, node_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取与指定节点相连的所有节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            包含源节点和目标节点的字典
        """
        edges = self.get_all_edges()
        sources = []
        targets = []
        
        for edge in edges:
            if edge['target'] == node_id:
                source_node = self.get_node_by_id(edge['source'])
                if source_node:
                    sources.append({
                        'node': source_node,
                        'edge': edge
                    })
            
            if edge['source'] == node_id:
                target_node = self.get_node_by_id(edge['target'])
                if target_node:
                    targets.append({
                        'node': target_node,
                        'edge': edge
                    })
        
        return {
            'sources': sources,  # 指向当前节点的节点
            'targets': targets   # 当前节点指向的节点
        }
    
    def clone_node(self, node_id: str, x_offset: int = 50, y_offset: int = 50) -> Optional[str]:
        """
        克隆节点
        
        Args:
            node_id: 要克隆的节点ID
            x_offset: X坐标偏移量
            y_offset: Y坐标偏移量
            
        Returns:
            新节点的ID，如果克隆失败则返回None
        """
        node = self.get_node_by_id(node_id)
        if not node:
            return None
        
        # 创建新节点
        new_node_id = self.add_node(
            text=node['value'],
            x=int(node['x']) + x_offset if 'x' in node else 0 + x_offset,
            y=int(node['y']) + y_offset if 'y' in node else 0 + y_offset,
            width=int(node['width']) if 'width' in node else 120,
            height=int(node['height']) if 'height' in node else 60,
            style=node['style'],
            parent_id=node['parent']
        )
        
        return new_node_id

# 示例用法
if __name__ == "__main__":
    # 创建扩展编辑器实例
    editor = DrawIOEditorExtended()
    
    # 添加一个节点
    node_id = editor.add_node(
        text="测试节点",
        x=100,
        y=100,
        width=120,
        height=60
    )
    
    # 使用扩展方法获取节点信息
    node_info = editor.get_node_by_id(node_id)
    if node_info:
        print(f"节点信息: {node_info}")
    
    # 克隆节点
    cloned_id = editor.clone_node(node_id)
    if cloned_id:
        print(f"克隆节点ID: {cloned_id}")
    
    # 保存图表
    editor.save("extended_example.drawio")