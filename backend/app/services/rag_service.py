"""
RAG Service (Retrieval-Augmented Generation)
Combines semantic search with LLM generation for context-aware responses
"""

from typing import Any, AsyncGenerator, Dict, List, Optional

from loguru import logger

from app.services.embedding_service import get_embedding_service
from app.services.llm_service import get_llm_service


class RAGService:
    """
    RAG pipeline for context-aware question answering
    Retrieves relevant context from vector DB and generates responses using LLM
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.llm_service = get_llm_service()
        self.default_top_k = 5
        self.default_score_threshold = 0.7

    async def initialize(self) -> bool:
        """
        Initialize RAG service components

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize embedding service (creates Qdrant collection if needed)
            success = await self.embedding_service.initialize()
            if not success:
                logger.error("Failed to initialize embedding service")
                return False

            # Check LLM service health
            llm_healthy = await self.llm_service.check_health()
            if not llm_healthy:
                logger.warning("LLM service not available")
                # Continue anyway - might be starting up

            logger.info("RAG service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"RAG service initialization failed: {str(e)}")
            return False

    async def _retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context documents for query

        Args:
            query: User query
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            filters: Optional metadata filters

        Returns:
            List of relevant documents with scores
        """
        try:
            logger.info(f"Retrieving context for query: {query[:100]}...")

            results = await self.embedding_service.search_similar(
                query=query,
                limit=top_k,
                score_threshold=score_threshold,
                filter_dict=filters,
            )

            logger.info(f"Retrieved {len(results)} context documents")
            return results

        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return []

    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            text = doc.get("text", "")
            score = doc.get("score", 0.0)
            metadata = doc.get("metadata", {})

            # Add metadata if available
            meta_str = ""
            if metadata:
                meta_items = [f"{k}: {v}" for k, v in metadata.items()]
                meta_str = f" [{', '.join(meta_items)}]"

            context_parts.append(
                f"[Document {i}] (Relevance: {score:.2f}){meta_str}\n{text}"
            )

        return "\n\n".join(context_parts)

    def _build_prompt(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instructions: Optional[str] = None,
    ) -> str:
        """
        Build prompt for LLM with context and query

        Args:
            query: User query
            context: Retrieved context
            conversation_history: Optional conversation history
            system_instructions: Optional custom system instructions

        Returns:
            Complete prompt string
        """
        # Default system instructions
        if system_instructions is None:
            system_instructions = """You are an intelligent banking assistant with access to a knowledge base.
Your task is to provide accurate, helpful, and professional responses to banking-related questions.

Guidelines:
1. Use the provided context to answer questions accurately
2. If the context doesn't contain relevant information, say so clearly
3. Be concise but thorough in your responses
4. Use professional banking terminology when appropriate
5. If asked about transactions or account-specific information, remind users to log in or contact support
6. Never make up information - only use what's in the context or general banking knowledge
7. Be helpful and friendly while maintaining professionalism"""

        # Build conversation context if history provided
        conversation_context = ""
        if conversation_history:
            conv_parts = []
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conv_parts.append(f"{role.upper()}: {content}")
            conversation_context = "\n".join(conv_parts) + "\n\n"

        # Construct final prompt
        prompt = f"""{system_instructions}

---

CONTEXT INFORMATION:
{context}

---

{conversation_context}USER QUERY: {query}

ASSISTANT RESPONSE:"""

        return prompt

    async def generate_response(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instructions: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate RAG response for user query

        Args:
            query: User query
            top_k: Number of context documents to retrieve
            score_threshold: Minimum similarity score for retrieval
            filters: Optional metadata filters for retrieval
            conversation_history: Optional conversation history
            system_instructions: Optional custom system instructions
            temperature: LLM sampling temperature

        Returns:
            Dict with response, context documents, and metadata

        Example:
            result = await rag_service.generate_response(
                query="How do I apply for a loan?",
                filters={"type": "policy"}
            )
            print(result["response"])
            print(f"Used {len(result['context_documents'])} documents")
        """
        try:
            logger.info(f"Generating RAG response for: {query[:100]}...")

            # Step 1: Retrieve relevant context
            context_docs = await self._retrieve_context(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                filters=filters,
            )

            # Step 2: Format context
            context_text = self._format_context(context_docs)

            # Step 3: Build prompt
            prompt = self._build_prompt(
                query=query,
                context=context_text,
                conversation_history=conversation_history,
                system_instructions=system_instructions,
            )

            # Step 4: Generate response using LLM
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=temperature,
                stream=False,
            )

            logger.info("RAG response generated successfully")

            return {
                "response": response,
                "context_documents": context_docs,
                "num_context_docs": len(context_docs),
                "query": query,
            }

        except Exception as e:
            logger.error(f"RAG response generation failed: {str(e)}")
            raise

    async def generate_response_stream(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instructions: Optional[str] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming RAG response

        Args:
            query: User query
            top_k: Number of context documents to retrieve
            score_threshold: Minimum similarity score
            filters: Optional metadata filters
            conversation_history: Optional conversation history
            system_instructions: Optional custom instructions
            temperature: LLM sampling temperature

        Yields:
            Response chunks as they're generated

        Example:
            async for chunk in rag_service.generate_response_stream("What is a loan?"):
                print(chunk, end='', flush=True)
        """
        try:
            logger.info(f"Generating streaming RAG response for: {query[:100]}...")

            # Retrieve context
            context_docs = await self._retrieve_context(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                filters=filters,
            )

            # Format context and build prompt
            context_text = self._format_context(context_docs)
            prompt = self._build_prompt(
                query=query,
                context=context_text,
                conversation_history=conversation_history,
                system_instructions=system_instructions,
            )

            # Stream response from LLM
            async for chunk in self.llm_service.stream(
                prompt=prompt,
                temperature=temperature,
            ):
                yield chunk

            logger.info("Streaming RAG response completed")

        except Exception as e:
            logger.error(f"Streaming RAG response failed: {str(e)}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        use_context: bool = True,
        top_k: int = 3,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Chat with context augmentation

        Args:
            messages: Conversation history (list of {role, content} dicts)
            use_context: Whether to retrieve and use context
            top_k: Number of context documents
            score_threshold: Minimum similarity score
            filters: Optional metadata filters
            temperature: LLM sampling temperature

        Returns:
            Generated response

        Example:
            messages = [
                {"role": "system", "content": "You are a banking assistant"},
                {"role": "user", "content": "What is a savings account?"},
                {"role": "assistant", "content": "A savings account is..."},
                {"role": "user", "content": "How about interest rates?"}
            ]
            response = await rag_service.chat(messages)
        """
        try:
            if not messages:
                raise ValueError("Messages list cannot be empty")

            # Get last user message for context retrieval
            last_user_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break

            if not last_user_message:
                raise ValueError("No user message found in conversation")

            # Retrieve and inject context if enabled
            if use_context:
                context_docs = await self._retrieve_context(
                    query=last_user_message,
                    top_k=top_k,
                    score_threshold=score_threshold,
                    filters=filters,
                )

                if context_docs:
                    context_text = self._format_context(context_docs)

                    # Insert context as a system message
                    context_message = {
                        "role": "system",
                        "content": f"RELEVANT CONTEXT:\n{context_text}",
                    }

                    # Add context before last user message
                    messages.insert(-1, context_message)

            # Generate chat response
            response = await self.llm_service.chat(
                messages=messages,
                temperature=temperature,
                stream=False,
            )

            return response

        except Exception as e:
            logger.error(f"RAG chat failed: {str(e)}")
            raise

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        use_context: bool = True,
        top_k: int = 3,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat with context augmentation

        Args:
            messages: Conversation history
            use_context: Whether to retrieve context
            top_k: Number of context documents
            score_threshold: Minimum similarity score
            filters: Optional metadata filters
            temperature: LLM sampling temperature

        Yields:
            Response chunks

        Example:
            messages = [{"role": "user", "content": "Tell me about loans"}]
            async for chunk in rag_service.chat_stream(messages):
                print(chunk, end='', flush=True)
        """
        try:
            if not messages:
                raise ValueError("Messages list cannot be empty")

            # Get last user message
            last_user_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break

            # Retrieve context if enabled
            if use_context and last_user_message:
                context_docs = await self._retrieve_context(
                    query=last_user_message,
                    top_k=top_k,
                    score_threshold=score_threshold,
                    filters=filters,
                )

                if context_docs:
                    context_text = self._format_context(context_docs)
                    context_message = {
                        "role": "system",
                        "content": f"RELEVANT CONTEXT:\n{context_text}",
                    }
                    messages.insert(-1, context_message)

            # Stream chat response
            async for chunk in self.llm_service.chat_stream(
                messages=messages,
                temperature=temperature,
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Streaming RAG chat failed: {str(e)}")
            raise

    async def ingest_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> List[str]:
        """
        Ingest document into vector database with chunking

        Args:
            text: Document text
            metadata: Optional metadata (type, category, etc.)
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks

        Returns:
            List of document IDs

        Example:
            doc_ids = await rag_service.ingest_document(
                text="Long policy document...",
                metadata={"type": "policy", "category": "loans"}
            )
        """
        try:
            logger.info(f"Ingesting document (length: {len(text)})")

            # Split text into chunks
            chunks = self._chunk_text(text, chunk_size, chunk_overlap)
            logger.info(f"Split document into {len(chunks)} chunks")

            # Add chunk metadata
            chunk_metadata_list = []
            for i, chunk in enumerate(chunks):
                chunk_meta = metadata.copy() if metadata else {}
                chunk_meta["chunk_index"] = i
                chunk_meta["total_chunks"] = len(chunks)
                chunk_metadata_list.append(chunk_meta)

            # Store chunks with embeddings
            doc_ids = await self.embedding_service.store_batch_embeddings(
                texts=chunks,
                metadata_list=chunk_metadata_list,
            )

            logger.info(f"Ingested {len(doc_ids)} document chunks")
            return doc_ids

        except Exception as e:
            logger.error(f"Document ingestion failed: {str(e)}")
            raise

    def _chunk_text(
        self, text: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or exclamation
                sentence_end = max(
                    text.rfind(".", start, end),
                    text.rfind("?", start, end),
                    text.rfind("!", start, end),
                )
                if sentence_end > start:
                    end = sentence_end + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    async def check_health(self) -> Dict[str, Any]:
        """
        Check health of RAG service components

        Returns:
            Health status of all components
        """
        try:
            embedding_healthy = await self.embedding_service.check_health()
            llm_healthy = await self.llm_service.check_health()

            collection_info = await self.embedding_service.get_collection_info()

            return {
                "status": "healthy"
                if (embedding_healthy and llm_healthy)
                else "degraded",
                "embedding_service": "healthy" if embedding_healthy else "unhealthy",
                "llm_service": "healthy" if llm_healthy else "unhealthy",
                "vector_database": collection_info,
            }

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Global instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get singleton instance of RAG service

    Returns:
        RAGService instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
