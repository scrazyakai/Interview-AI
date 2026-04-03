import logging

from unstructured.partition.pdf import partition_pdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def process(file_path:str) -> list:
    #解析文档
    elements = partition_pdf(filename=file_path,strategy="fast")
    #提取文本
    texts = [el.text for el in elements if getattr(el,"text",None)]
    full_text = "\n".join(texts)

    # 创建文档切分器
    text_spliter = RecursiveCharacterTextSplitter(separators=["\n\n","\n"," ",""]
                                            ,chunk_size=256
                                            ,chunk_overlap=32)
    chunks = text_spliter.split_text(full_text)
    return chunks