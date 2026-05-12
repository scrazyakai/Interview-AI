import importlib
import sys
import types
import unittest
from unittest.mock import patch

from langchain_core.documents import Document


def _install_fake_dependencies() -> None:
    fake_hf_module = types.ModuleType("langchain_huggingface")
    fake_openai_module = types.ModuleType("langchain_openai")
    fake_pgvector_module = types.ModuleType("langchain_postgres")
    fake_config_module = types.ModuleType("app.core.config.config")

    class FakeHuggingFaceEmbeddings:
        def __init__(self, model_name: str, model_kwargs: dict, encode_kwargs: dict):
            self.model_name = model_name
            self.model_kwargs = model_kwargs
            self.encode_kwargs = encode_kwargs

    class FakeOpenAIEmbeddings:
        def __init__(self, model: str, api_key: str, base_url: str, dimensions: int | None = None):
            self.model = model
            self.api_key = api_key
            self.base_url = base_url
            self.dimensions = dimensions

    class FakeVectorStore:
        def __init__(self, *, embedding=None, collection_name=None, connection=None):
            self.embedding = embedding
            self.collection_name = collection_name
            self.connection = connection
            self.added_documents = []

        def add_documents(self, documents):
            self.added_documents.extend(documents)

    class FakePGVector:
        last_init_call = None
        last_from_existing_index_call = None

        def __init__(
            self,
            *,
            embeddings,
            collection_name,
            connection,
            use_jsonb,
            pre_delete_collection,
        ):
            type(self).last_init_call = {
                "embeddings": embeddings,
                "collection_name": collection_name,
                "connection": connection,
                "use_jsonb": use_jsonb,
                "pre_delete_collection": pre_delete_collection,
            }
            self.embedding = embeddings
            self.collection_name = collection_name
            self.connection = connection
            self.use_jsonb = use_jsonb
            self.pre_delete_collection = pre_delete_collection
            self.added_documents = []

        def add_documents(self, documents):
            self.added_documents.extend(documents)

        @classmethod
        def from_existing_index(
            cls,
            *,
            embedding,
            collection_name,
            connection,
            use_jsonb,
        ):
            cls.last_from_existing_index_call = {
                "embedding": embedding,
                "collection_name": collection_name,
                "connection": connection,
                "use_jsonb": use_jsonb,
            }
            return FakeVectorStore(
                embedding=embedding,
                collection_name=collection_name,
                connection=connection,
            )

    fake_hf_module.HuggingFaceEmbeddings = FakeHuggingFaceEmbeddings
    fake_openai_module.OpenAIEmbeddings = FakeOpenAIEmbeddings
    fake_pgvector_module.PGVector = FakePGVector
    fake_config_module.settings = types.SimpleNamespace(
        DATABASE_URL="postgresql://default:pass@localhost:5432/interview_ai",
        PGVECTOR_CONNECTION_STRING=None,
        EMBEDDING_PROVIDER="huggingface",
        EMBEDDING_MODEL_NAME="default-embedding-model",
        EMBEDDING_BASE_URL=None,
        EMBEDDING_API_KEY=None,
        EMBEDDING_DIMENSION=None,
    )

    sys.modules["langchain_huggingface"] = fake_hf_module
    sys.modules["langchain_openai"] = fake_openai_module
    sys.modules["langchain_postgres"] = fake_pgvector_module
    sys.modules["app.core.config.config"] = fake_config_module


_install_fake_dependencies()
sys.modules.pop("app.rag.embedding_model", None)
sys.modules.pop("app.rag.index_construction", None)
embedding_model_module = importlib.import_module("app.rag.embedding_model")
index_construction = importlib.import_module("app.rag.index_construction")

EmbeddingModel = embedding_model_module.EmbeddingModel
IndexConstructionModule = index_construction.IndexConstructionModule
PGVector = index_construction.PGVector
BizException = index_construction.BizException
ErrorCode = index_construction.ErrorCode
settings = index_construction.settings


class EmbeddingModelTests(unittest.TestCase):
    def test_huggingface_embedding_uses_settings_model_by_default(self) -> None:
        with patch.object(settings, "EMBEDDING_PROVIDER", "huggingface"), patch.object(
            settings,
            "EMBEDDING_MODEL_NAME",
            "bge-small-test",
        ):
            embedding = EmbeddingModel().create()

        self.assertEqual(embedding.model_name, "bge-small-test")
        self.assertEqual(embedding.model_kwargs["device"], "cuda")
        self.assertTrue(embedding.encode_kwargs["normalize_embeddings"])

    def test_aliyun_compatible_embedding_uses_openai_compatible_client(self) -> None:
        with patch.object(settings, "EMBEDDING_PROVIDER", "aliyun_compatible"), patch.object(
            settings,
            "EMBEDDING_MODEL_NAME",
            "text-embedding-v3",
        ), patch.object(
            settings,
            "EMBEDDING_API_KEY",
            "test-api-key",
        ), patch.object(
            settings,
            "EMBEDDING_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ), patch.object(
            settings,
            "EMBEDDING_DIMENSION",
            1024,
        ):
            embedding = EmbeddingModel().create()

        self.assertEqual(embedding.model, "text-embedding-v3")
        self.assertEqual(embedding.api_key, "test-api-key")
        self.assertEqual(
            embedding.base_url,
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.assertEqual(embedding.dimensions, 1024)


class IndexConstructionModuleTest(unittest.TestCase):
    def test_init_sets_up_embeddings_and_normalizes_connection(self) -> None:
        with patch.object(settings, "EMBEDDING_PROVIDER", "huggingface"):
            module = IndexConstructionModule(
                model_name="test-model",
                collection_name="test-collection",
                connection_string="postgresql+asyncpg://user:pass@localhost:5432/interview_ai",
            )

        self.assertIsNotNone(module.embeddings)
        self.assertEqual(module.embeddings.model_name, "test-model")
        self.assertEqual(module.collection_name, "test-collection")
        self.assertEqual(
            module.connection_string,
            "postgresql+psycopg://user:pass@localhost:5432/interview_ai",
        )

    def test_init_uses_settings_connection_when_argument_missing(self) -> None:
        with patch.object(settings, "PGVECTOR_CONNECTION_STRING", None), patch.object(
            settings,
            "DATABASE_URL",
            "postgresql://user:pass@localhost:5432/interview_ai",
        ):
            module = IndexConstructionModule()

        self.assertEqual(
            module.connection_string,
            "postgresql+psycopg://user:pass@localhost:5432/interview_ai",
        )

    def test_init_prefers_pgvector_connection_from_settings(self) -> None:
        with patch.object(
            settings,
            "PGVECTOR_CONNECTION_STRING",
            "postgresql://pgvector:pass@localhost:5432/vector_db",
        ), patch.object(
            settings,
            "DATABASE_URL",
            "postgresql://user:pass@localhost:5432/interview_ai",
        ):
            module = IndexConstructionModule()

        self.assertEqual(
            module.connection_string,
            "postgresql+psycopg://pgvector:pass@localhost:5432/vector_db",
        )

    def test_build_vector_index_raises_for_empty_chunks(self) -> None:
        module = IndexConstructionModule(
            connection_string="postgresql://user:pass@localhost:5432/interview_ai"
        )

        with self.assertRaises(BizException) as ctx:
            module.build_vector_index([])

        self.assertEqual(ctx.exception.code, ErrorCode.CHUNCK_IS_NONE)

    def test_build_vector_index_builds_and_persists_pgvector_collection(self) -> None:
        module = IndexConstructionModule(
            collection_name="question_bank",
            connection_string="postgresql://user:pass@localhost:5432/interview_ai",
            pre_delete_collection=True,
        )
        chunks = [
            Document(page_content="题目一", metadata={"question_title": "Q1"}),
            Document(page_content="题目二", metadata={"question_title": "Q2"}),
        ]

        vectorstore = module.build_vector_index(chunks)

        self.assertIs(module.vectorstore, vectorstore)
        self.assertIs(PGVector.last_init_call["embeddings"], module.embeddings)
        self.assertEqual(PGVector.last_init_call["collection_name"], "question_bank")
        self.assertEqual(
            PGVector.last_init_call["connection"],
            "postgresql+psycopg://user:pass@localhost:5432/interview_ai",
        )
        self.assertTrue(PGVector.last_init_call["use_jsonb"])
        self.assertTrue(PGVector.last_init_call["pre_delete_collection"])
        self.assertEqual(module.vectorstore.added_documents, chunks)

    def test_load_index_loads_existing_pgvector_collection(self) -> None:
        module = IndexConstructionModule(
            collection_name="question_bank",
            connection_string="postgresql://user:pass@localhost:5432/interview_ai",
        )

        loaded = module.load_index()

        self.assertIs(module.vectorstore, loaded)
        self.assertEqual(PGVector.last_from_existing_index_call["collection_name"], "question_bank")
        self.assertEqual(
            PGVector.last_from_existing_index_call["connection"],
            "postgresql+psycopg://user:pass@localhost:5432/interview_ai",
        )
        self.assertIs(PGVector.last_from_existing_index_call["embedding"], module.embeddings)
        self.assertTrue(PGVector.last_from_existing_index_call["use_jsonb"])


if __name__ == "__main__":
    unittest.main()
