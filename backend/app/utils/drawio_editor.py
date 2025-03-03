import xml.etree.ElementTree as ET
import uuid
from typing import Dict, Optional, List, Tuple, Any, Union

class DrawIOEditor:
    """DrawIO文件编辑器
    
    提供对DrawIO文件的解析、编辑和保存功能，支持节点的增删改查操作。
    """
    
    def __init__(self, file_path: str = None, content: str = None):
        """初始化编辑器
        
        Args:
            file_path: DrawIO文件路径
            content: DrawIO XML内容字符串
        """
        self.file_path = file_path
        
        if content:
            # 从字符串加载XML
            self.root = ET.fromstring(content)
            self.tree = None
        elif file_path:
            # 从文件加载XML
            self.tree = ET.parse(file_path)
            self.root = self.tree.getroot()
        else:
            # 创建新的空白文档
            self.root = self._create_empty_diagram()
            self.tree = None
        
        # 缓存常用元素
        self._diagram = self._find_first_diagram()
        self._graph_model = self._find_graph_model()
        self._root_element = self._find_root_element()
        
        # 获取默认的父节点ID (通常是ID为1的节点)
        self._default_parent_id = self._find_default_parent_id()
    
    def _create_empty_diagram(self) -> ET.Element:
        """创建空白的DrawIO文档结构"""
        mxfile = ET.Element('mxfile')
        diagram = ET.SubElement(mxfile, 'diagram', id=str(uuid.uuid4()))
        graph_model = ET.SubElement(diagram, 'mxGraphModel')
        root = ET.SubElement(graph_model, 'root')
        
        # 添加必要的根节点
        ET.SubElement(root, 'mxCell', id="0")
        ET.SubElement(root, 'mxCell', id="1", parent="0")
        
        return mxfile
    
    def _find_first_diagram(self) -> Optional[ET.Element]:
        """查找第一个diagram元素"""
        return self.root.find('.//diagram')
    
    def _find_graph_model(self) -> Optional[ET.Element]:
        """查找mxGraphModel元素"""
        return self.root.find('.//mxGraphModel')
    
    def _find_root_element(self) -> Optional[ET.Element]:
        """查找root元素"""
        return self.root.find('.//root')
    
    def _find_default_parent_id(self) -> str:
        """查找默认的父节点ID"""
        # 通常是ID为1的节点
        default_parent = self.root.find('.//mxCell[@id="1"]')
        if default_parent is not None:
            return "1"
        return "0"  # 如果找不到，返回根节点ID
    
    def find_element_by_id(self, element_id: str) -> Optional[ET.Element]:
        """通过ID查找元素
        
        Args:
            element_id: 元素ID
            
        Returns:
            找到的元素，如果未找到则返回None
        """
        return self.root.find(f'.//*[@id="{element_id}"]')
    
    def find_elements_by_value(self, value: str) -> List[ET.Element]:
        """通过值查找元素
        
        Args:
            value: 元素值
            
        Returns:
            找到的元素列表
        """
        return self.root.findall(f'.//*[@value="{value}"]')
    
    def get_next_id(self) -> str:
        """获取下一个可用的ID
        
        Returns:
            新的唯一ID
        """
        # 使用UUID生成唯一ID
        return str(uuid.uuid4())
    
    def add_node(self, 
                 text: str, 
                 x: int, 
                 y: int, 
                 width: int = 120, 
                 height: int = 60, 
                 style: str = "rounded=1;whiteSpace=wrap;html=1;", 
                 parent_id: str = None) -> str:
        """添加新节点
        
        Args:
            text: 节点文本
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
            style: 样式字符串
            parent_id: 父节点ID，如果为None则使用默认父节点
            
        Returns:
            新节点的ID
        """
        if parent_id is None:
            parent_id = self._default_parent_id
        
        # 生成新的ID
        node_id = self.get_next_id()
        
        # 创建新节点
        cell = ET.Element('mxCell', 
            id=node_id, 
            value=text,
            style=style,
            parent=parent_id,
            vertex="1"
        )
        
        # 添加几何信息
        # 使用字典传递属性，处理'as'关键字
        geom_attrs = {
            'x': str(x),
            'y': str(y),
            'width': str(width),
            'height': str(height),
            'as': 'geometry'
        }
        geometry = ET.SubElement(cell, 'mxGeometry', **geom_attrs)

        
        # 将节点添加到root元素
        if self._root_element is not None:
            self._root_element.append(cell)
        
        return node_id
    
    def add_edge(self, 
                source_id: str, 
                target_id: str, 
                label: str = "", 
                style: str = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;", 
                parent_id: str = None) -> str:
        """添加连接线
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            label: 连接线标签
            style: 样式字符串
            parent_id: 父节点ID，如果为None则使用默认父节点
            
        Returns:
            新连接线的ID
        """
        if parent_id is None:
            parent_id = self._default_parent_id
        
        # 生成新的ID
        edge_id = self.get_next_id()
        
        # 创建连接线
        cell = ET.Element('mxCell', 
            id=edge_id, 
            value=label,
            style=style,
            parent=parent_id,
            source=source_id,
            target=target_id,
            edge="1"
        )
        
        # 添加几何信息
        # 使用字典传递属性，处理'as'关键字
        geom_attrs = {
            'relative': "1",
            'as': 'geometry'
        }
        geometry = ET.SubElement(cell, 'mxGeometry', **geom_attrs)
        
        # 将连接线添加到root元素
        if self._root_element is not None:
            self._root_element.append(cell)
        
        return edge_id
    
    def update_node(self, 
                   node_id: str, 
                   text: Optional[str] = None, 
                   style: Optional[str] = None, 
                   x: Optional[int] = None, 
                   y: Optional[int] = None, 
                   width: Optional[int] = None, 
                   height: Optional[int] = None) -> bool:
        """更新节点属性
        
        Args:
            node_id: 节点ID
            text: 新的节点文本，如果为None则不更新
            style: 新的样式字符串，如果为None则不更新
            x: 新的X坐标，如果为None则不更新
            y: 新的Y坐标，如果为None则不更新
            width: 新的宽度，如果为None则不更新
            height: 新的高度，如果为None则不更新
            
        Returns:
            是否更新成功
        """
        node = self.find_element_by_id(node_id)
        if node is None:
            return False
        
        # 更新节点属性
        if text is not None:
            node.set('value', text)
        
        if style is not None:
            node.set('style', style)
        
        # 更新几何信息
        if any(param is not None for param in [x, y, width, height]):
            geometry = node.find('./mxGeometry')
            if geometry is not None:
                if x is not None:
                    geometry.set('x', str(x))
                if y is not None:
                    geometry.set('y', str(y))
                if width is not None:
                    geometry.set('width', str(width))
                if height is not None:
                    geometry.set('height', str(height))
        
        return True
    
    def delete_element(self, element_id: str) -> bool:
        """删除元素
        
        Args:
            element_id: 元素ID
            
        Returns:
            是否删除成功
        """
        element = self.find_element_by_id(element_id)
        if element is None:
            return False
        
        # 查找父元素
        for parent in self.root.iter():
            for child in list(parent):
                if child.get('id') == element_id:
                    parent.remove(child)
                    return True
        
        return False
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """获取所有节点信息
        
        Returns:
            节点信息列表
        """
        nodes = []
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            node_info = {
                'id': cell.get('id'),
                'value': cell.get('value', ''),
                'style': cell.get('style', ''),
                'parent': cell.get('parent', '')
            }
            
            # 获取几何信息
            geometry = cell.find('./mxGeometry')
            if geometry is not None:
                node_info['x'] = geometry.get('x')
                node_info['y'] = geometry.get('y')
                node_info['width'] = geometry.get('width')
                node_info['height'] = geometry.get('height')
            
            nodes.append(node_info)
        
        return nodes
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """获取所有连接线信息
        
        Returns:
            连接线信息列表
        """
        edges = []
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            edge_info = {
                'id': cell.get('id'),
                'value': cell.get('value', ''),
                'style': cell.get('style', ''),
                'parent': cell.get('parent', ''),
                'source': cell.get('source', ''),
                'target': cell.get('target', '')
            }
            
            edges.append(edge_info)
        
        return edges
    
    def apply_diff_patches(self, patches: List[Dict[str, Any]]) -> bool:
        """应用差异补丁
        
        Args:
            patches: 补丁列表，每个补丁是一个字典，包含操作类型和相关参数
            
        Returns:
            是否应用成功
        """
        success = True
        for patch in patches:
            operation = patch.get('operation')
            
            if operation == 'add_node':
                self.add_node(
                    text=patch.get('text', ''),
                    x=patch.get('x', 0),
                    y=patch.get('y', 0),
                    width=patch.get('width', 120),
                    height=patch.get('height', 60),
                    style=patch.get('style', ''),
                    parent_id=patch.get('parent_id')
                )
            elif operation == 'add_edge':
                self.add_edge(
                    source_id=patch.get('source_id', ''),
                    target_id=patch.get('target_id', ''),
                    label=patch.get('label', ''),
                    style=patch.get('style', ''),
                    parent_id=patch.get('parent_id')
                )
            elif operation == 'update_node':
                success = success and self.update_node(
                    node_id=patch.get('node_id', ''),
                    text=patch.get('text'),
                    style=patch.get('style'),
                    x=patch.get('x'),
                    y=patch.get('y'),
                    width=patch.get('width'),
                    height=patch.get('height')
                )
            elif operation == 'delete_element':
                success = success and self.delete_element(
                    element_id=patch.get('element_id', '')
                )
        
        return success
    
    def save(self, output_path: Optional[str] = None) -> None:
        """保存DrawIO文件
        
        Args:
            output_path: 输出文件路径，如果为None则使用初始化时的文件路径
        """
        save_path = output_path or self.file_path
        if save_path is None:
            raise ValueError("必须提供输出文件路径")
        
        if self.tree is not None:
            self.tree.write(save_path, encoding='utf-8', xml_declaration=True)
        else:
            # 如果是从字符串加载的，需要创建一个新的ElementTree
            tree = ET.ElementTree(self.root)
            tree.write(save_path, encoding='utf-8', xml_declaration=True)
    
    def to_string(self) -> str:
        """将DrawIO文档转换为XML字符串
        
        Returns:
            XML字符串
        """
        from xml.dom import minidom
        rough_string = ET.tostring(self.root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
    
    def _ensure_mxfile_wrapped(self, content: str) -> str:
        """确保内容被<mxfile>标签包裹
        
        Args:
            content: DrawIO XML内容
            
        Returns:
            包裹后的内容
        """
        if not content.strip().startswith('<mxfile'):
            content = f"<mxfile>{content}</mxfile>"
        return content
    
    def parse_tree_by_level(self, start_level: int = 0, end_level: int = 3, max_token: int = 1000, iterable: bool = False) -> str:
        """按层级解析DrawIO文件树形结构
        
        Args:
            start_level: 开始解析的层级，0表示根节点
            end_level: 结束解析的层级
            max_token: 最大字符数限制，超过此限制将截断并添加省略号
            iterable: 是否在字符数较少时自动增加解析深度
            
        Returns:
            解析后的树形结构字符串
        """
        result = []
        token_count = 0
        
        def _get_element_level(element: ET.Element, parent_map: Dict) -> int:
            """获取元素的层级深度"""
            level = 0
            current = element
            while current in parent_map and parent_map[current] is not None:
                current = parent_map[current]
                level += 1
            return level
        
        def _format_element(element: ET.Element, level: int) -> str:
            """格式化元素为字符串表示"""
            indent = '  ' * level
            tag = element.tag
            attrs = ' '.join([f'{k}="{v}"' for k, v in element.attrib.items()])
            
            # 检查元素是否有子元素
            has_children = len(element) > 0
            # 检查元素是否有文本内容
            has_text = element.text and element.text.strip()
            # 检查元素是否有尾部文本（可能包含注释）
            has_tail = element.tail and element.tail.strip()
            
            # 构建基本标签
            if attrs:
                base_tag = f"<{tag} {attrs}"
            else:
                base_tag = f"<{tag}"
            
            # 如果有子元素或文本内容
            if has_children or has_text:
                # 有子元素或文本，返回开始标签
                result = f"{indent}{base_tag}>"
                # 如果有文本内容，添加到结果中
                if has_text:
                    result += element.text
                
                # 如果有子元素，递归处理子元素
                if has_children:
                    # 先添加换行，准备添加子元素
                    result += "\n"
                    # 递归处理所有子元素
                    for child in element:
                        # 将子元素添加到已处理集合中
                        processed_elements.add(child)
                        # 递归调用，增加缩进级别
                        child_str = _format_element(child, level + 1)
                        result += child_str + "\n"
                    # 添加闭合标签，与开始标签保持相同缩进
                    result += f"{indent}</{tag}>"
                else:
                    # 没有子元素但有文本，直接添加闭合标签
                    result += f"</{tag}>"
            else:
                # 没有子元素和文本，返回自闭合标签
                result = f"{indent}{base_tag}/>"
            
            # 如果有尾部文本（可能包含注释），添加到结果中
            if has_tail:
                result += element.tail
                
            return result
        
        # 构建父节点映射
        parent_map = {child: parent for parent in self.root.iter() for child in parent}
        
        # 遍历元素树并构建完整的XML结构
        dynamic_end_level = end_level
        processed_elements = set()
        
        def process_element(element, current_level):
            nonlocal token_count
            if element in processed_elements or current_level > dynamic_end_level:
                return
            
            processed_elements.add(element)
            level_diff = current_level - start_level
            
            if start_level <= current_level <= dynamic_end_level:
                # 添加开始标签
                element_str = _format_element(element, level_diff)
                result.append(element_str)
                token_count += len(element_str)
                
                # 检查是否超出最大字符数限制
                if token_count >= max_token:
                    result.append("...")
                    return
        
        # 遍历所有元素，但只处理指定层级的元素，避免重复处理
        elements_by_level = {}
        
        # 首先按层级分组所有元素
        for element in self.root.iter():
            level = _get_element_level(element, parent_map)
            if level not in elements_by_level:
                elements_by_level[level] = []
            elements_by_level[level].append(element)
        
        # 处理指定层级范围内的元素
        for level in range(start_level, dynamic_end_level + 1):
            if level in elements_by_level:
                for element in elements_by_level[level]:
                    # 如果启用迭代并且当前字符数较少，动态增加解析深度
                    if iterable and token_count < max_token * 0.7 and level > end_level:
                        dynamic_end_level = level
                    
                    # 只处理尚未处理过的元素
                    if element not in processed_elements:
                        process_element(element, level)
        
        return "\n".join(result)
    
    def parse_diagram_by_level(self, start_level: int = 0, end_level: int = 3, max_token: int = 1000, iterable: bool = False) -> str:
        """按层级解析DrawIO图表结构
        
        与parse_tree_by_level不同，此方法专注于图表的逻辑结构而非XML结构
        
        Args:
            start_level: 开始解析的层级，0表示根节点
            end_level: 结束解析的层级
            max_token: 最大字符数限制，超过此限制将截断并添加省略号
            iterable: 是否在字符数较少时自动增加解析深度
            
        Returns:
            解析后的图表结构字符串
        """
        result = []
        token_count = 0
        
        # 获取所有节点和边
        nodes = self.get_all_nodes()
        edges = self.get_all_edges()
        
        # 构建节点层级关系
        node_levels = {}
        node_map = {node['id']: node for node in nodes}
        
        # 计算节点层级
        for node in nodes:
            level = 0
            current_id = node['id']
            parent_id = node['parent']
            
            # 向上追溯父节点计算层级
            while parent_id and parent_id != '0' and parent_id != '1':
                level += 1
                if parent_id in node_map:
                    parent_id = node_map[parent_id]['parent']
                else:
                    break
            
            node_levels[current_id] = level
        
        # 处理节点
        dynamic_end_level = end_level
        for node in nodes:
            level = node_levels.get(node['id'], 0)
            
            # 如果启用迭代并且当前字符数较少，动态增加解析深度
            if iterable and token_count < max_token * 0.7 and level > end_level:
                dynamic_end_level = level
            
            if start_level <= level <= dynamic_end_level:
                indent = '  ' * (level - start_level)
                node_str = f"{indent}节点: {node['value']} (ID: {node['id']})"
                result.append(node_str)
                token_count += len(node_str)
                
                # 检查是否超出最大字符数限制
                if token_count >= max_token:
                    result.append("...")
                    break
        
        # 处理边（连接线）
        if token_count < max_token:
            result.append("\n连接关系:")
            token_count += 10
            
            for edge in edges:
                source_id = edge['source']
                target_id = edge['target']
                
                if source_id in node_map and target_id in node_map:
                    source_level = node_levels.get(source_id, 0)
                    target_level = node_levels.get(target_id, 0)
                    
                    # 只显示在指定层级范围内的连接
                    if (start_level <= source_level <= dynamic_end_level or 
                        start_level <= target_level <= dynamic_end_level):
                        source_value = node_map[source_id]['value']
                        target_value = node_map[target_id]['value']
                        edge_str = f"  {source_value} -> {target_value} {edge['value']}"
                        result.append(edge_str)
                        token_count += len(edge_str)
                        
                        # 检查是否超出最大字符数限制
                        if token_count >= max_token:
                            result.append("...")
                            break
        
        return "\n".join(result)
    
    def apply_diff_patches(self, patches: List[Dict[str, Any]]) -> bool:
        """应用差异补丁
        
        Args:
            patches: 补丁列表，每个补丁是一个字典，包含操作类型和相关参数
            
        Returns:
            是否应用成功
        """
        success = True
        for patch in patches:
            operation = patch.get('operation')
            
            if operation == 'add_node':
                self.add_node(
                    text=patch.get('text', ''),
                    x=patch.get('x', 0),
                    y=patch.get('y', 0),
                    width=patch.get('width', 120),
                    height=patch.get('height', 60),
                    style=patch.get('style', ''),
                    parent_id=patch.get('parent_id')
                )
            elif operation == 'add_edge':
                self.add_edge(
                    source_id=patch.get('source_id', ''),
                    target_id=patch.get('target_id', ''),
                    label=patch.get('label', ''),
                    style=patch.get('style', ''),
                    parent_id=patch.get('parent_id')
                )
            elif operation == 'update_node':
                success = success and self.update_node(
                    node_id=patch.get('node_id', ''),
                    text=patch.get('text'),
                    style=patch.get('style'),
                    x=patch.get('x'),
                    y=patch.get('y'),
                    width=patch.get('width'),
                    height=patch.get('height')
                )
            elif operation == 'delete_element':
                success = success and self.delete_element(
                    element_id=patch.get('element_id', '')
                )
        
        return success
    
    def save(self, output_path: Optional[str] = None) -> None:
        """保存DrawIO文件
        
        Args:
            output_path: 输出文件路径，如果为None则使用初始化时的文件路径
        """
        save_path = output_path or self.file_path
        if save_path is None:
            raise ValueError("必须提供输出文件路径")
        
        if self.tree is not None:
            self.tree.write(save_path, encoding='utf-8', xml_declaration=True)
        else:
            # 如果是从字符串加载的，需要创建一个新的ElementTree
            tree = ET.ElementTree(self.root)
            tree.write(save_path, encoding='utf-8', xml_declaration=True)
    
    def to_string(self) -> str:
        """将DrawIO文档转换为XML字符串
        
        Returns:
            XML字符串
        """
        from xml.dom import minidom
        rough_string = ET.tostring(self.root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
    
    def _ensure_mxfile_wrapped(self, content: str) -> str:
        """确保内容被<mxfile>标签包裹
        
        Args:
            content: DrawIO XML内容
            
        Returns:
            包裹后的内容
        """
        if not content.strip().startswith('<mxfile'):
            content = f"<mxfile>{content}</mxfile>"
        return content