import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Any, Union
from app.utils.drawio_editor import DrawIOEditor
# from llm.dash_deepseek import DeepseekLLM
from app.llm.glm import GLMLLM

class DrawIOXMLProcessor:
    """
    DrawIO XML处理器
    
    提供基于大模型的DrawIO XML元素提取、替换和新增功能
    """
    
    def __init__(self, llm_service=None):
        """
        初始化处理器
        
        Args:
            llm_service: 大语言模型服务，用于生成代码
        """
        self.llm_service = llm_service
    
    def extract_xml_by_level(self, file_path: str, start_level: int = 4, end_level: int = 10) -> str:
        """
        按层级提取DrawIO XML元素
        
        Args:
            file_path: DrawIO文件路径
            start_level: 开始解析的层级
            end_level: 结束解析的层级
            
        Returns:
            提取的XML元素字符串
        """
        editor = DrawIOEditor(file_path=file_path)
        return editor.parse_tree_by_level(start_level=start_level, end_level=end_level, max_token=5000, iterable=True)
    
    def generate_optimized_xml(self, xml_content: str, user_requirement: str) -> str:
        """
        生成优化后的XML内容
        
        Args:
            xml_content: 原始XML内容
            user_requirement: 用户优化需求
            
        Returns:
            优化后的XML内容
        """
        prompt = self._create_optimization_prompt(xml_content, user_requirement)
        
        if self.llm_service:
            response = self.llm_service.chat(prompt)
            return self._extract_code_from_response(response.answer_content)
        else:
            # 如果没有提供LLM服务，返回原始内容（仅用于测试）
            return xml_content
    
    def _create_optimization_prompt(self, xml_content: str, user_requirement: str) -> str:
        """
        创建优化提示词
        
        Args:
            xml_content: 原始XML内容
            user_requirement: 用户优化需求
            
        Returns:
            优化提示词
        """
        return f"""
你是一个专业的DrawIO图表优化助手，请根据以下需求优化DrawIO图表的XML代码：

用户需求：
{user_requirement}

当前XML内容：
```xml
{xml_content}
```

请按以下要求进行优化：
1. 保持所有现有元素的ID不变
2. 可以修改元素的属性、样式和位置，若修改某个具有id元素，则必须包含其完整的子元素。
3. 可以添加新的元素（新元素需要有新的ID,新的边也需要有id）
5. 如果元素需要删除，则输出<delete id="元素ID"/>
4. 如果元素无需修改，则无需输出对应的元素。我们仅输出需要修改的元素和删除的标记即可。
4. 输出优化后XML代码，使用```xml和```包裹

请确保输出的XML代码格式正确，可以被DrawIO正常解析。
"""
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        从响应中提取代码块
        
        Args:
            response: LLM响应内容
            
        Returns:
            提取的代码块
        """
        # 使用正则表达式提取代码块
        pattern = r'```xml\s*([\s\S]*?)\s*```'
        match = re.search(pattern, response)
        if match:
            return match.group(1).strip()
        return ""
    
    def replace_elements_by_id(self, original_file_path: str, optimized_xml: str, output_file_path: str) -> Dict[str, Any]:
        """
        根据ID替换元素
        
        Args:
            original_file_path: 原始DrawIO文件路径
            optimized_xml: 优化后的XML内容
            output_file_path: 输出文件路径
            
        Returns:
            包含替换结果的字典
        """
        # 加载原始文件
        original_editor = DrawIOEditor(file_path=original_file_path)
        original_tree = original_editor.tree
        original_root = original_editor.root
        
        # 解析优化后的XML
        try:
            # 处理删除标记，将<delete id="元素ID"/>转换为可解析的XML格式
            delete_pattern = r'<delete id="([^"]+)"/>'
            delete_ids = re.findall(delete_pattern, optimized_xml)
            print(f"删除的元素ID：{delete_ids}")
            # 移除删除标记，以便正常解析其他XML元素
            cleaned_xml = re.sub(delete_pattern, '', optimized_xml)
            
            # 修复XML格式问题 - 确保所有标签都正确闭合
            # 检查是否有mxGeometry标签没有正确闭合
            # cleaned_xml = re.sub(r'<mxGeometry([^>]*)>\s*</mxCell>', r'<mxGeometry\1></mxGeometry></mxCell>', cleaned_xml)
            # 确保所有自闭合标签格式正确
            # cleaned_xml = re.sub(r'<([^\s>]+)([^>]*)>\s*</\1>', r'<\1\2></\1>', cleaned_xml)
            # 移除可能导致解析错误的独立mxGeometry标签
            # cleaned_xml = re.sub(r'\s*<mxGeometry([^>]*)/>(\s*(?!</mxCell>))', '', cleaned_xml)
            # 移除重复的mxGeometry标签
            # cleaned_xml = re.sub(r'(<mxGeometry[^>]*>[^<]*</mxGeometry>)\s*\1', r'\1', cleaned_xml)
            # 修复错误的结束标签，如</mxGeometry>没有对应的开始标签
            # cleaned_xml = re.sub(r'([^<]*)</mxGeometry>(\s*</mxCell>)', r'\1\2', cleaned_xml)
            print(f"优化后的XML内容：\n{cleaned_xml}")
            try:
                optimized_elements = ET.fromstring(f"<root>{cleaned_xml}</root>")
            except ET.ParseError as e:
                # 如果解析失败，尝试更严格的XML修复
                print(f"初次解析失败: {str(e)}，尝试修复XML...")
                # 将不完整的标签转换为自闭合标签
                pattern = r'<(mxGeometry[^>]*?)>(?![\s\S]*?</mxGeometry>)'
                cleaned_xml = re.sub(pattern, r'<\1/>', cleaned_xml)
                # 移除所有孤立的结束标签
                cleaned_xml = re.sub(r'</mxGeometry>(?!\s*</mxCell>)', '', cleaned_xml)
                optimized_elements = ET.fromstring(f"<root>{cleaned_xml}</root>")
        except ET.ParseError as e:
            return {
                "success": False,
                "message": f"解析优化后的XML失败: {str(e)}",
                "replaced_count": 0,
                "added_count": 0,
                "deleted_count": 0
            }
        
        replaced_count = 0
        added_count = 0
        deleted_count = 0
        added_ids = []
        deleted_ids = []
        
        # 处理需要删除的元素
        for element_id in delete_ids:
            original_element = original_editor.find_element_by_id(element_id)
            if original_element is not None:
                parent = self._find_parent_element(original_root, original_element)
                if parent is not None:
                    parent.remove(original_element)
                    deleted_count += 1
                    deleted_ids.append(element_id)
        
        # 遍历优化后的元素
        for element in optimized_elements:
            element_id = element.get('id')
            
            if element_id:
                # 查找原始元素
                original_element = original_editor.find_element_by_id(element_id)
                
                if original_element is not None:
                    # 替换现有元素
                    parent = self._find_parent_element(original_root, original_element)
                    if parent is not None:
                        # 记录元素在父元素中的位置
                        index = list(parent).index(original_element)
                        # 删除原始元素
                        parent.remove(original_element)
                        # 在相同位置插入新元素
                        parent.insert(index, element)
                        replaced_count += 1
                else:
                    # 添加新元素
                    root_element = original_editor._root_element
                    if root_element is not None:
                        root_element.append(element)
                        added_count += 1
                        added_ids.append(element_id)
        
        # 保存修改后的文件
        original_tree.write(output_file_path, encoding='utf-8', xml_declaration=True)
        
        return {
            "success": True,
            "message": f"成功替换 {replaced_count} 个元素，新增 {added_count} 个元素，删除 {deleted_count} 个元素",
            "replaced_count": replaced_count,
            "added_count": added_count,
            "deleted_count": deleted_count,
            "added_ids": added_ids,
            "deleted_ids": deleted_ids
        }
    
    def _find_parent_element(self, root: ET.Element, element: ET.Element) -> Optional[ET.Element]:
        """
        查找元素的父元素
        
        Args:
            root: 根元素
            element: 要查找父元素的元素
            
        Returns:
            父元素，如果未找到则返回None
        """
        for parent in root.iter():
            for child in list(parent):
                if child == element:
                    return parent
        return None


def main():
    """
    主函数
    """
    # 文件路径
    # input_path = os.path.join(os.path.dirname(__file__), 'examples', 'rag_advanced.drawio')
    # output_path = os.path.join(os.path.dirname(__file__), 'examples', 'rag_optimized_new.drawio')
    input_path = os.path.join(os.path.dirname(__file__), 'examples', 'example.drawio')
    output_path = os.path.join(os.path.dirname(__file__), 'examples', 'example_new.drawio')
    
    # 初始化处理器 - 测试时不使用LLM服务
    processor = DrawIOXMLProcessor(llm_service=GLMLLM())
    
    # 1. 提取XML元素
    xml_content = processor.extract_xml_by_level(input_path, start_level=4, end_level=10)
    print(f"提取的XML元素:\n{xml_content}\n")
    
    # 2. 生成优化后的XML
    user_requirement = "优化流程图变成一个RAG的流程图，去除无用的节点和边，添加更多细节和连接。"
    optimized_xml = processor.generate_optimized_xml(xml_content, user_requirement)
    print(f"优化后的XML:\n{optimized_xml}\n")
    
    # 3. 替换元素
    result = processor.replace_elements_by_id(input_path, optimized_xml, output_path)
    print(f"替换结果: {result['message']}")
    if result['added_count'] > 0:
        print(f"新增元素ID: {', '.join(result['added_ids'])}")
    if result.get('deleted_count', 0) > 0:
        print(f"删除元素ID: {', '.join(result['deleted_ids'])}")


if __name__ == "__main__":
    main()