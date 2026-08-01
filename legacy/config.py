"""
Anime Script AI - Configuration Module
Centralized configuration for all services
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration"""
    url: str = "postgresql://anime_ai:anime_ai_pass@localhost:5432/anime_script_db"
    
    @property
    def async_url(self) -> str:
        return self.url.replace("postgresql://", "postgresql+asyncpg://")


@dataclass
class QdrantConfig:
    """Qdrant vector database configuration"""
    url: str = "http://localhost:6333"
    api_key: Optional[str] = None
    collection_name: str = "anime_chunks"
    vector_size: int = 1024  # BGE-M3 embedding dimension
    distance: str = "Cosine"


@dataclass
class Neo4jConfig:
    """Neo4j knowledge graph configuration"""
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "anime_ai_pass"


@dataclass
class ElasticsearchConfig:
    """Elasticsearch BM25 search configuration"""
    url: str = "http://localhost:9200"
    index_name: str = "anime_chunks"


@dataclass
class RedisConfig:
    """Redis cache configuration"""
    url: str = "redis://localhost:6379/0"
    max_memory: str = "2gb"
    eviction_policy: str = "allkeys-lru"


@dataclass
class OllamaConfig:
    """Ollama LLM server configuration"""
    url: str = "http://localhost:11434"
    model_name: str = "qwen2.5-72b-instruct-q4_k_m"
    
    @property
    def openai_url(self) -> str:
        return f"{self.url}/v1"


@dataclass
class EmbeddingConfig:
    """Embedding model configuration"""
    model_name: str = "BAAI/bge-m3"
    device: str = "cuda"  # RTX 5090
    max_length: int = 8192  # BGE-M3 context length


@dataclass
class ChunkerConfig:
    """Text chunking configuration"""
    chunk_size: int = 512  # tokens
    overlap: int = 64  # tokens
    separator: str = "\n\n"


@dataclass
class RetrievalConfig:
    """Retrieval pipeline configuration"""
    qdrant_top_k: int = 50
    elasticsearch_top_k: int = 30
    reranker_top_k: int = 10
    final_context_chunks: int = 8


@dataclass
class LangGraphConfig:
    """LangGraph agent pipeline configuration"""
    max_research_retries: int = 3
    max_script_writer_retries: int = 2
    fact_check_threshold: float = 0.80
    quality_review_threshold: float = 0.75


@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Service configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    elasticsearch: ElasticsearchConfig = field(default_factory=ElasticsearchConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    chunker: ChunkerConfig = field(default_factory=ChunkerConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    langgraph: LangGraphConfig = field(default_factory=LangGraphConfig)


# Global config instance
config = AppConfig()
