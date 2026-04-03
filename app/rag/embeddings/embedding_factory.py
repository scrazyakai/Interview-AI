import os

from dotenv import load_dotenv
import logging
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

load_dotenv()
model_name = os.getenv("EMBEDDING_MODEL_NAME","BAAI/bge-small-zh-v1.5")

def get_embedding_model():
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    logger.info(f"Loading embedding model from {model_name}")
    return embeddings