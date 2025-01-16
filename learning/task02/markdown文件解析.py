from llama_index.core.node_parser import MarkdownNodeParser
# 导入 Markdown Reader
from llama_index.readers.file import MarkdownReader

# 创建 Markdown 解析器实例
parser = MarkdownNodeParser()

# 创建 Markdown Reader 实例
reader = MarkdownReader()

markdown_docs = reader.load_data(file="data/plantuml.md")

# 从 Markdown 文档中获取节点
nodes = parser.get_nodes_from_documents(markdown_docs)

for node in nodes:
    print(node.text)
    print(node.metadata)
    input("-"*100)