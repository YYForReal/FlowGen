import os
from dotenv import load_dotenv
import networkx as nx
from pyvis.network import Network
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from metagpt.tools.tool_registry import register_tool

# 加载.env文件中的环境变量
load_dotenv()


@register_tool(
    tags=["graph", "neo4j graph"],
    include_functions=[
        "__init__",
        "add_documents_to_graph",
        "show_graph",
        "get_schema",
        "get_subgraph",
        "custom_query",
    ],
)
class GraphController:
    """A controller for managing and visualizing graphs using Neo4j."""

    def __init__(self):
        """Initialize the GraphController with Neo4j connection."""
        self.graph = Neo4jGraph()

    def add_documents_to_graph(self, graph_documents, llm):
        """Add documents to the graph.

        Args:
            graph_documents (list): List of documents to add to the graph.
            llm (LLM): Language model instance for transformation.
        """
        llm_transformer = LLMGraphTransformer(llm=llm)
        graph_documents = llm_transformer.convert_to_graph_documents(graph_documents)
        self.graph.add_graph_documents(
            graph_documents, base_entity_label=True, include_source=True
        )

    def get_schema(self):
        """Get the schema of the graph."""
        self.graph.refresh_schema()
        return self.graph.get_schema

    def get_subgraph(self, node_id: str, depth: int = 1, output_html: str = ""):
        """Get the subgraph of a node up to a certain depth.

        Args:
            node_id (str): The ID of the starting node.
            depth (int): The depth of the subgraph to retrieve. Default is 1.
            output_html (str): The path to save the visualized subgraph as an HTML file. Default is an empty string

        Returns:
            list: List of relationships in the subgraph.
        """
        cypher = f"""
        MATCH (n {{id: '{node_id}'}})-[r*1..{depth}]-(m)
        RETURN n, r, m
        """
        result = self.graph.query(cypher)

        relationships = []
        G = nx.MultiDiGraph()

        for record in result:
            source = record["n"]
            target = record["m"]
            rels = record["r"]

            for rel in rels:
                relationships.append(rel)
                G.add_edge(source["id"], target["id"], label=rel)

        # Visualize the graph and save to HTML if specified
        if output_html:
            if not output_html.endswith(".html"):
                raise ValueError("Output file must be an HTML file")
            net = Network(notebook=False, directed=True)
            net.from_nx(G)
            net.show(output_html)

        return relationships

    def custom_query(self, cypher: str):
        """Execute a custom Cypher query and return the results.

        Args:
            cypher (str): The custom Cypher query to execute.

        Returns:
            list: List of query results.
        """
        result = self.graph.query(cypher)
        return result
