# 嵌入（向量）存储

!!! note
   `EmbeddingStore` 可以实现 `searchAsync(...)`，以便从非阻塞 AI 服务使用时不会阻塞线程。未实现它的存储仍然可以使用，
   但前提是检索器通过 `offloadBlocking(true)` 选择卸载阻塞操作；否则调用会大声失败，而不是静默阻塞。
   另请参阅 [非阻塞与响应式](non-blocking.md)。


有关向量存储的文档可在[此处](rag.md#向量存储embedding-store)找到。

所有受支持的向量存储可在[此处](../integrations/embedding-stores/index.md)找到。

## 示例
- [使用内存向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/embedding/store/InMemoryEmbeddingStoreExample.java)
- [使用 Chroma 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/chroma-example/src/main/java/ChromaEmbeddingStoreExample.java)
- [使用 Elasticsearch 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/elasticsearch-example/src/main/java/ElasticsearchEmbeddingStoreExample.java)
- [使用 Milvus 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/milvus-example/src/main/java/MilvusEmbeddingStoreExample.java)
- [使用 Neo4j 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/neo4j-example/src/main/java/Neo4jEmbeddingStoreExample.java)
- [使用 OpenSearch 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/opensearch-example/src/main/java/OpenSearchEmbeddingStoreExample.java)
- [使用 Pinecone 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/pinecone-example/src/main/java/PineconeEmbeddingStoreExample.java)
- [使用 Qdrant 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/qdrant-example/src/main/java/QdrantEmbeddingStoreExample.java)
- [使用 Redis 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/redis-example/src/main/java/RedisEmbeddingStoreExample.java)
- [使用 Vespa 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/vespa-example/src/main/java/VespaEmbeddingStoreExample.java)
- [使用 Weaviate 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/weaviate-example/src/main/java/WeaviateEmbeddingStoreExample.java)
- [使用 PGVector 向量存储的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/pgvector-example/src/main/java/PgVectorEmbeddingStoreExample.java)
