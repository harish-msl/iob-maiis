"""
Embedding Service
Handles text vectorization using Ollama embeddings and Qdrant vector database
"""

import hashlib
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.core.config import get_settings

settings = get_settings()


class EmbeddingService:
    """
    Service for generating and managing text embeddings
    Integrates with Ollama for embedding generation and Qdrant for storage
    """

    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.qdrant_host = settings.QDRANT_HOST
        self.qdrant_port = settings.QDRANT_PORT
        self.collection_name = "banking_documents"
        self.embedding_dim = 768  # nomic-embed-text dimension
        self.client: Optional[QdrantClient] = None
        self.timeout = aiohttp.ClientTimeout(total=60)

    async def initialize(self) -> bool:
        """
        Initialize Qdrant client and create collection if needed

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                host=self.qdrant_host,
                port=self.qdrant_port,
                timeout=60,
            )

            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {str(e)}")
            return False

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Ollama

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)

        Raises:
            Exception: If embedding generation fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []

        try:
            logger.debug(f"Generating embedding for text (length: {len(text)})")

            payload = {
                "model": self.embedding_model,
                "prompt": text.strip(),
            }

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.ollama_url}/api/embeddings",
                    json=payload,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Embedding API error: {error_text}")
                        raise Exception(f"Embedding API error: {response.status}")

                    data = await response.json()
                    embedding = data.get("embedding", [])

                    if not embedding:
                        raise Exception("Empty embedding returned from API")

                    logger.debug(
                        f"Generated embedding with dimension: {len(embedding)}"
                    )
                    return embedding

        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error during embedding: {str(e)}")
            raise Exception(f"Failed to connect to embedding service: {str(e)}")
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Example:
            texts = ["What is a loan?", "How to open an account?"]
            embeddings = await service.generate_batch_embeddings(texts)
        """
        embeddings = []
        for text in texts:
            try:
                embedding = await self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed text: {str(e)}")
                embeddings.append([])

        return embeddings

    def _generate_id(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate unique ID for a document based on content

        Args:
            text: Document text
            metadata: Optional metadata

        Returns:
            Unique document ID (hash)
        """
        content = text
        if metadata:
            content += str(sorted(metadata.items()))

        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def store_embedding(
        self,
        text: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None,
    ) -> str:
        """
        Store text embedding in Qdrant vector database

        Args:
            text: Original text
            embedding: Pre-computed embedding (if None, will generate)
            metadata: Optional metadata to store with embedding
            document_id: Optional custom document ID

        Returns:
            Document ID in Qdrant

        Example:
            doc_id = await service.store_embedding(
                text="Loan application policy...",
                metadata={"type": "policy", "category": "loans"}
            )
        """
        try:
            if not self.client:
                await self.initialize()

            # Generate embedding if not provided
            if embedding is None:
                embedding = await self.generate_embedding(text)

            if not embedding:
                raise Exception("Failed to generate embedding")

            # Generate ID if not provided
            if document_id is None:
                document_id = self._generate_id(text, metadata)

            # Prepare payload
            payload = {
                "text": text,
                "timestamp": str(metadata.get("timestamp"))
                if metadata and "timestamp" in metadata
                else None,
            }

            if metadata:
                payload.update(metadata)

            # Store in Qdrant
            point = PointStruct(
                id=document_id,
                vector=embedding,
                payload=payload,
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            logger.info(f"Stored embedding with ID: {document_id}")
            return document_id

        except Exception as e:
            logger.error(f"Failed to store embedding: {str(e)}")
            raise

    async def store_batch_embeddings(
        self,
        texts: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Store multiple embeddings in batch

        Args:
            texts: List of texts
            embeddings: Optional pre-computed embeddings
            metadata_list: Optional list of metadata dicts

        Returns:
            List of document IDs

        Example:
            texts = ["Policy 1", "Policy 2"]
            metadata = [{"type": "policy"}, {"type": "policy"}]
            ids = await service.store_batch_embeddings(texts, metadata_list=metadata)
        """
        try:
            if not self.client:
                await self.initialize()

            # Generate embeddings if not provided
            if embeddings is None:
                embeddings = await self.generate_batch_embeddings(texts)

            if metadata_list is None:
                metadata_list = [{}] * len(texts)

            # Prepare points
            points = []
            doc_ids = []

            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                if not embedding:
                    logger.warning(f"Skipping text {i} due to empty embedding")
                    continue

                metadata = metadata_list[i] if i < len(metadata_list) else {}
                doc_id = self._generate_id(text, metadata)

                payload = {"text": text}
                if metadata:
                    payload.update(metadata)

                points.append(
                    PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload=payload,
                    )
                )
                doc_ids.append(doc_id)

            # Batch upsert
            if points:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
                logger.info(f"Stored {len(points)} embeddings in batch")

            return doc_ids

        except Exception as e:
            logger.error(f"Failed to store batch embeddings: {str(e)}")
            raise

    async def search_similar(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic similarity

        Args:
            query: Search query text
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)
            filter_dict: Optional metadata filters

        Returns:
            List of similar documents with scores

        Example:
            results = await service.search_similar(
                query="How to apply for a loan?",
                limit=3,
                filter_dict={"type": "policy"}
            )

            for result in results:
                print(f"Score: {result['score']}")
                print(f"Text: {result['text']}")
        """
        try:
            if not self.client:
                await self.initialize()

            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            if not query_embedding:
                raise Exception("Failed to generate query embedding")

            # Prepare filter if provided
            query_filter = None
            if filter_dict:
                conditions = []
                for key, value in filter_dict.items():
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value),
                        )
                    )
                query_filter = models.Filter(must=conditions)

            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
            )

            # Format results
            results = []
            for hit in search_results:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
                }
                results.append(result)

            logger.info(f"Found {len(results)} similar documents for query")
            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            raise

    async def delete_embedding(self, document_id: str) -> bool:
        """
        Delete embedding from vector database

        Args:
            document_id: ID of document to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                await self.initialize()

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[document_id],
                ),
            )

            logger.info(f"Deleted embedding: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete embedding: {str(e)}")
            return False

    async def delete_batch_embeddings(self, document_ids: List[str]) -> bool:
        """
        Delete multiple embeddings in batch

        Args:
            document_ids: List of document IDs to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                await self.initialize()

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=document_ids,
                ),
            )

            logger.info(f"Deleted {len(document_ids)} embeddings")
            return True

        except Exception as e:
            logger.error(f"Failed to delete batch embeddings: {str(e)}")
            return False

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the vector collection

        Returns:
            Collection statistics and configuration
        """
        try:
            if not self.client:
                await self.initialize()

            collection_info = self.client.get_collection(self.collection_name)

            return {
                "name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "segments_count": collection_info.segments_count,
                "status": collection_info.status,
                "config": {
                    "dimension": self.embedding_dim,
                    "distance": "cosine",
                },
            }

        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return {}

    async def check_health(self) -> bool:
        """
        Check if embedding service and Qdrant are healthy

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check Ollama embedding endpoint
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status != 200:
                        return False

            # Check Qdrant
            if not self.client:
                await self.initialize()

            collections = self.client.get_collections()

            logger.info("Embedding service is healthy")
            return True

        except Exception as e:
            logger.error(f"Embedding service health check failed: {str(e)}")
            return False


# Global instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get singleton instance of embedding service

    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
