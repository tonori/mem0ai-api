import dotenv
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from typenv import Env

dotenv.load_dotenv()
env = Env()

vector_config = VectorStoreConfig(
    provider="qdrant",
    config={
        "host": "127.0.0.1",
        "port": 6333,
    }
).dict()

llm_config = LlmConfig(
    provider="openai",
    config={
        "model": env.str("OPENAI_MODEL")
    }
).dict()

embedding_config = EmbedderConfig(
    provider="openai",
    config={
        "model": env.str("OPENAI_EMBEDDING_MODEL")
    }
).dict()


