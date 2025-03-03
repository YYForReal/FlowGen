import os
import json
import glob
import pickle
import logging
from typing import List, Any
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from models.chat_glm4 import glm4v_summarize_image
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import TokenTextSplitter

# 设置日志配置
if not os.path.exists("output"):
    os.makedirs("output")

# read config.json output_path
with open("config.json", "r") as f:
    config = json.load(f)
    output_path = config["output_path"] or "output/output.log"

logging.basicConfig(
    filename=output_path,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:%(message)s",
)

class PDFRAGProcessor:
    def __init__(self, config_path: str):
        # 读取配置文件
        with open(config_path, "r") as f:
            config = json.load(f)
        self.pdf_dir = config["pdf_dir"]
        self.image_output_dir = config["image_output_dir"]
        self.embedding_api_key = config["embedding_api_key"]
        self.model_api_key = config["model_api_key"]
        self.model_url = config["model_url"]
        self.model_name = config["model"]
        self.retriever_path = config["retriever_path"]
        self.vllm_model_api_key = config["vllm_model_api_key"]
        self.vllm_model_url = config["vllm_model_url"]

        self.text_elements = []
        self.table_elements = []
        self.image_summaries = []

        self.summary_cache = "output/summary_cache.json"
        self.docstore_cache = "output/docstore_cache.pkl"
        self.load_summary_cache()

        # 获取PDF目录中的所有PDF文件路径
        self.pdf_paths = glob.glob(os.path.join(self.pdf_dir, "*.pdf"))

        # 确保输出目录存在
        if not os.path.exists(self.image_output_dir):
            os.makedirs(self.image_output_dir)

    def load_summary_cache(self):
        if os.path.exists(self.summary_cache):
            with open(self.summary_cache, "r") as f:
                self.summary_data = json.load(f)
        else:
            self.summary_data = {}

    def save_summary_cache(self):
        with open(self.summary_cache, "w") as f:
            json.dump(self.summary_data, f, ensure_ascii=False, indent=4)

    def partition_pdf(self, pdf_path: str, extract_images: bool = True,max_characters: int = 4000, new_after_n_chars=3800,combine_text_under_n_chars=2000):
        logging.info(f"Partitioning PDF: {pdf_path}")
        image_dir = os.path.join(self.image_output_dir, os.path.basename(pdf_path))
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        raw_pdf_elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            extract_images_in_pdf=extract_images,
            # image_output_dir_path=image_dir, # 这个和下面的是冲突的，如果不单独输出，就存在meta_data里面。
            extract_image_block_to_payload=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=max_characters,
            new_after_n_chars=new_after_n_chars,
            combine_text_under_n_chars=combine_text_under_n_chars,
        )
        self.categorize_elements(raw_pdf_elements)

    def categorize_elements(self, elements):
        logging.info(f"Categorizing elements from PDF")

        class Element(BaseModel):
            type: str
            text: Any

        categorized_elements = []
        for element in elements:
            if "unstructured.documents.elements.Table" in str(type(element)):
                categorized_elements.append(Element(type="table", text=str(element)))
            elif "unstructured.documents.elements.CompositeElement" in str(
                type(element)
            ):
                categorized_elements.append(Element(type="text", text=str(element)))

        self.table_elements.extend(
            [e for e in categorized_elements if e.type == "table"]
        )
        self.text_elements.extend([e for e in categorized_elements if e.type == "text"])

    def generate_summaries(self):
        logging.info("Generating summaries for text and tables")
        prompt_text = """You are an assistant tasked with summarizing tables and text. \
Give a concise summary of the table or text. Table or text chunk: {element} """
        prompt = ChatPromptTemplate.from_template(prompt_text)

        model = ChatOpenAI(
            temperature=0.1,
            model=self.model_name,
            base_url=self.model_url,
            openai_api_key=self.model_api_key,
        )

        summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()

        texts = [i.text for i in self.text_elements]
        text_summaries = []
        for text in texts:
            try:
                if text in self.summary_data:
                    text_summaries.append(self.summary_data[text])
                    logging.info(f"Using cached summary for text: {text}")
                else:
                    summary = summarize_chain.invoke({"element": text})
                    text_summaries.append(summary)
                    self.summary_data[text] = summary
                    logging.info(f"Generated new summary for text: {text}")
            except Exception as e:
                logging.error(f"Error summarizing text: {text}")
                print(e)

        tables = [i.text for i in self.table_elements]
        table_summaries = []
        for table in tables:
            try:
                if table in self.summary_data:
                    table_summaries.append(self.summary_data[table])
                    logging.info(f"Using cached summary for table: {table}")
                else:
                    summary = summarize_chain.invoke({"element": table})
                    table_summaries.append(summary)
                    self.summary_data[table] = summary
                    logging.info(f"Generated new summary for table: {table}")
            except Exception as e:
                logging.error(f"Error summarizing table: {table}")
                print(e)

        self.save_summary_cache()

        return text_summaries, table_summaries

    def summarize_images(self, reuse=True):
        logging.info("Summarizing images")
        img_paths = glob.glob(os.path.join(self.image_output_dir, "*.jpg"))
        img_summaries = []

        for img_path in img_paths:
            summary_path = img_path.replace(".jpg", ".txt")

            if reuse and os.path.exists(summary_path):
                with open(summary_path, "r") as f:
                    summary = f.read().strip()
                    logging.info(f"Reusing summary for {img_path}")
            else:
                summary = glm4v_summarize_image(img_path)
                if summary:
                    with open(summary_path, "w") as f:
                        f.write(summary)
                    logging.info(f"Generated and saved summary for {img_path}")

            if summary:
                img_summaries.append(summary)

        self.image_summaries = img_summaries
        if not self.image_summaries:
            logging.warning("图片摘要列表为空，请检查图片摘要生成过程。")

    def process_pdfs(self):
        logging.info("Starting PDFRAGProcessor run")

        for pdf_path in self.pdf_paths:
            self.partition_pdf(pdf_path)

        text_summaries, table_summaries = self.generate_summaries()
        self.summarize_images()

        documents = []
        documents.extend([Document(page_content=s) for s in text_summaries])
        documents.extend([Document(page_content=s) for s in table_summaries])
        documents.extend([Document(page_content=s) for s in self.image_summaries])

        logging.info("PDFRAGProcessor run completed")
        return documents


def load_documents(directory_path):
    loader = DirectoryLoader(directory_path)
    documents = loader.load()
    return documents

def chunk_documents(documents, chunk_size=512, chunk_overlap=12):
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_documents = text_splitter.split_documents(documents)
    return chunked_documents

if __name__ == "__main__":
    processor = PDFRAGProcessor(config_path="config.json")
    pdf_documents = processor.process_pdfs()
    
    directory_documents = load_documents('path_to_your_directory')
    chunked_directory_documents = chunk_documents(directory_documents)
    
    # 在这里可以添加处理或组合 pdf_documents 和 chunked_directory_documents 的代码
    